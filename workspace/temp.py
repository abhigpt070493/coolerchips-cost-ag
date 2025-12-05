from pathlib import Path

output_path = Path(__file__).parent / "outputs"

def plot_total_cost_box(file_paths, output_dir: Path | None = None, filename: str = 'total_cost_boxplot.png', n_modules_mw: float = 1.0):
    """Create a box-style comparison chart for total cost across scenarios.

    Args:
        file_paths: iterable of CSV file paths (proc_total_* style) containing a 'Total' row and
                    columns: Total_mean, Total_std, Total_min, Total_max.
        output_dir: directory to save plot; defaults to sibling 'outputs'.
        filename: output PNG filename.
        n_modules_mw: multiplier applied to all costs prior to plotting.

    Behavior:
        - Scenarios labeled Scenario 1, Scenario 2, ... in order of file_paths.
        - Box body spans mean ± 2*std (95% CI).
        - Whiskers drawn in two segments: min→(mean-2*std) and (mean+2*std)→max (do not pass through box).
        - Mean value labeled inside box (center) in currency format.
        - Y axis labeled 'Cost ($/MW)' and formatted as currency.
        - Title: 'MPHX Cost Estimates'.
    """
    if output_dir is None:
        output_dir = Path(__file__).parent / 'outputs'
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker

    records = []
    for i, fp in enumerate(file_paths, start=1):
        fp = Path(fp)
        if not fp.exists():
            raise FileNotFoundError(f"Input file not found: {fp}")
        df = pd.read_csv(fp)
        # Attempt to locate Total row (Process == 'Total')
        total_row = None
        if 'Process' in df.columns:
            total_candidates = df[df['Process'].astype(str) == 'Total']
            if not total_candidates.empty:
                total_row = total_candidates.iloc[0]
        if total_row is None:
            raise ValueError(f"No 'Total' row found in file: {fp}")
        # Extract metrics with fallbacks and scale
        mean = total_row.get('Total_mean', total_row.get('Total', None))
        if mean is None:
            raise ValueError(f"Mean (Total_mean/Total) not found in file: {fp}")
        mean = float(mean) * n_modules_mw
        std = float(total_row.get('Total_std', 0.0)) * n_modules_mw
        tmin = float(total_row.get('Total_min', (float(mean) - 2 * float(std)) / max(n_modules_mw, 1e-9))) * n_modules_mw if 'Total_min' in total_row else (mean - 2 * std)
        tmax = float(total_row.get('Total_max', (float(mean) + 2 * float(std)) / max(n_modules_mw, 1e-9))) * n_modules_mw if 'Total_max' in total_row else (mean + 2 * std)
        records.append({
            'label': f'Scenario {i}',
            'mean': mean,
            'std': std,
            'min': tmin,
            'max': tmax
        })

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    currency_fmt = mticker.FuncFormatter(lambda x, pos: f'${x:,.0f}')

    box_width = 0.6
    for idx, rec in enumerate(records):
        mean = rec['mean']
        std = rec['std']
        low = mean - 2 * std
        high = mean + 2 * std
        if high < low:
            low, high = high, low
        # Whiskers as two segments (avoid drawing through box)
        if rec['min'] < low:
            ax.vlines(idx, rec['min'], low, colors='#4c92c3', linewidth=2, zorder=3)
        if rec['max'] > high:
            ax.vlines(idx, high, rec['max'], colors='#4c92c3', linewidth=2, zorder=3)
        # Box body (opaque with requested RGB blue)
        height = max(0.0, high - low)
        ax.add_patch(plt.Rectangle((idx - box_width / 2, low), box_width, height,
                                   facecolor='#4c92c3', edgecolor='#4c92c3', linewidth=1.0, zorder=3))
        # Mean label (currency)
        ax.text(idx, mean, f"${int(round(mean)):,}", ha='center', va='center', color='black', fontsize=10, fontweight='bold', zorder=4)

    ax.set_xticks(range(len(records)))
    ax.set_xticklabels([r['label'] for r in records])
    ax.set_ylabel('Cost ($/MW)')
    ax.set_title('MPHX Cost Estimates')
    ax.yaxis.set_major_formatter(currency_fmt)
    # Subtle horizontal grid lines behind plot elements
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color='#dddddd', linestyle='-', linewidth=0.7, alpha=0.8, zorder=0)

    # Adjust y-limits with padding
    all_vals = [v for r in records for v in (r['min'], r['max'])]
    ymin = min(all_vals) if all_vals else 0
    ymax = max(all_vals) if all_vals else 1
    pad = (ymax - ymin) * 0.08 if ymax > ymin else ymax * 0.1 + 1
    ax.set_ylim(max(0, ymin - pad), ymax + pad)

    plt.tight_layout()
    out_path = output_dir / filename
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    return out_path

plot_total_cost_box([output_path/"proc_total_2025-11-06_19-35-26_lw.csv",output_path/"proc_total_2025-11-06_19-35-26_gl.csv",output_path/"proc_total_2025-11-06_19-40-45_lw.csv",output_path/"proc_total_2025-11-06_19-40-45_gl.csv",output_path/"proc_total_2025-11-06_19-27-55_lw.csv",output_path/"proc_total_2025-11-06_19-27-55_gl.csv"],output_path, n_modules_mw=112)