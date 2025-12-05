from __future__ import annotations

import json
import random
import shutil
import tempfile
from pathlib import Path
from typing import Any
import importlib
import os

import pandas as pd
import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from typing import Dict


def _sample_node(node: Any, level: str) -> Any:
    """Recursively sample a JSON node.

    If a dict contains numeric 'low' and 'high' keys, sample uniformly between them.
    - If that dict also contains 'base', replace 'base' with the sampled value and return the dict.
    - Otherwise return the sampled numeric value (replacing the dict itself).
    """
    if isinstance(node, dict):
        # Detect range-like dict
        if 'low' in node and 'high' in node and isinstance(node['low'], (int, float)) and isinstance(node['high'], (int, float)):
            sampled = random.uniform(float(node['low']), float(node['high']))
            # Prefer writing sampled value into the requested level if present
            if level in node:
                new = dict(node)
                new[level] = sampled
                return new
            # Fallback: write into base if it exists
            if 'base' in node:
                new = dict(node)
                new['base'] = sampled
                return new
            # Otherwise return scalar sampled value
            return sampled
        # Otherwise recurse through keys
        return {k: _sample_node(v, level) for k, v in node.items()}
    elif isinstance(node, list):
        return [_sample_node(v, level) for v in node]
    else:
        return node


def _collect_json_files(input_root: Path):
    return list(input_root.rglob('*.json'))


def monte_carlo_run(scenario_name: str, join_method: str, ann_prod_vol: int, n_sim: int, level: str = "base") -> pd.DataFrame:
    """Run Monte Carlo simulations and return summary DataFrame.

    Behavior:
    - Loads all JSON files under the project's `input_data` directory.
    - For each simulation, samples any JSON value that is a dict containing numeric 'low' and 'high' keys.
      - If the dict also contains a 'base' key (common for price objects), the sampled value replaces 'base'.
      - Otherwise the dict itself is replaced with the sampled numeric value.
    - Writes the sampled input tree to a temporary input_data directory and runs the selected scenario's
      `create_hx` function (from `analyses.iterations.mphx_sabic` or `mphx_oct24`) using that input.
    - Runs the cost pipeline to produce a per-process cost DataFrame for each simulation.
    - Returns a summary DataFrame with mean and std for each cost item grouped by Process.

    Args:
        scenario_name: 'mphx_sabic' or 'mphx_oct24'
        join_method: passed to create_hx
        ann_prod_vol: annual production volume used in Scenario
        n_sim: number of simulations

    Returns:
        pd.DataFrame with columns like 'Process', '<Metric>_mean', '<Metric>_std'
    """
    # Resolve repository paths based on this file's location
    repo_root = Path(__file__).resolve().parents[1]
    input_root = repo_root / 'input_data'
    if not input_root.exists():
        raise FileNotFoundError(f"input_data directory not found at expected location: {input_root}")

    # Map scenario name to module path
    scenario_map = {
        'mphx_sabic': 'analyses.iterations.mphx_sabic',
        'mphx_oct24': 'analyses.iterations.mphx_oct24',
    }
    if scenario_name not in scenario_map:
        raise ValueError(f"Unknown scenario_name {scenario_name}; supported: {list(scenario_map.keys())}")

    module_name = scenario_map[scenario_name]
    scenario_module = importlib.import_module(module_name)
    # Ensure fresh import to avoid any state caching
    importlib.reload(scenario_module)

    # Prepare temporary working tree: a workspace directory whose ../input_data will point to temp_input
    tmp_root = Path(tempfile.mkdtemp(prefix='mc_mphx_'))
    tmp_input = tmp_root / 'input_data'
    tmp_workspace = tmp_root / 'workspace'
    tmp_input.mkdir(parents=True)
    tmp_workspace.mkdir(parents=True)

    # Copy input tree structure to temp once (we'll overwrite files per simulation)
    for src in _collect_json_files(input_root):
        rel = src.relative_to(input_root)
        dst = tmp_input / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    all_sim_dfs = []

    # We'll import the pipeline functions we need from the analyses module that live in repo
    from analyses.Scenario import Scenario
    from analyses.cost_output import calc_cost_obj, conv_cost_to_df

    # For each simulation draw
    for i in range(n_sim):
        # Sample all JSON files and write to temp input
        for src in _collect_json_files(input_root):
            rel = src.relative_to(input_root)
            dst = tmp_input / rel
            with open(src, 'r') as f:
                text = f.read()
                try:
                    data = json.loads(text)
                except Exception:
                    # Try stripping comment lines starting with // or #
                    lines = [ln for ln in text.splitlines() if not ln.strip().startswith('//') and not ln.strip().startswith('#')]
                    try:
                        data = json.loads('\n'.join(lines))
                    except Exception:
                        # If still can't parse, copy the original file unchanged
                        shutil.copy2(src, dst)
                        continue
            sampled = _sample_node(data, level)
            # Write sampled JSON
            with open(dst, 'w') as f:
                json.dump(sampled, f, indent=2)

        # Run model using the temporary workspace as CWD so that create_hx's '../input_data' resolves
        # to our tmp_input directory
        old_cwd = Path.cwd()
        try:
            os.chdir(tmp_workspace)
            # reload module so that any internal caches referencing files are refreshed
            scenario_module = importlib.reload(scenario_module)
            # call create_hx with explicit level so sampled JSON 'base' fields are used
            create_hx = getattr(scenario_module, 'create_hx')
            model_hx, mfg_process, over, fac = create_hx(join_method=join_method, level=level)

            # Build scenario and run cost pipeline
            baseline = Scenario(ann_prod_vol, model_hx, mfg_process, over, fac)
            cost_bd = calc_cost_obj(baseline)
            df = conv_cost_to_df(mfg_process, cost_bd)
            df['sim'] = i
            all_sim_dfs.append(df)
            # update progress bar after finishing this simulation
            _print_progress(i+1, n_sim)
        finally:
            os.chdir(old_cwd)

    # Clean up temporary tree
    try:
        shutil.rmtree(tmp_root)
    except Exception:
        pass

    # ensure progress bar ends with newline
    print()

    # Concatenate results and compute mean/std per process
    df_all = pd.concat(all_sim_dfs, ignore_index=True)
    numeric_cols = [c for c in df_all.columns if c not in ['Process', 'sim']]

    # Per-process metrics: mean, std, min, max for each numeric column
    grouped = df_all.groupby('Process')[numeric_cols].agg(['mean', 'std', 'min', 'max'])
    # Flatten multiindex columns
    grouped.columns = [f"{col}_{stat}" for col, stat in grouped.columns]
    grouped = grouped.reset_index()

    # --- New outputs requested ---
    # 1) Per-process total cost mean/std (Total column aggregated per process)
    if 'Total' in df_all.columns:
        proc_total = df_all.groupby('Process')['Total'].agg(['mean', 'std', 'min', 'max']).reset_index()
        proc_total.columns = ['Process', 'Total_mean', 'Total_std', 'Total_min', 'Total_max']
    else:
        # If no Total column exists, sum numeric_cols to compute a total per Process per sim then aggregate
        tmp = df_all.copy()
        tmp['Total_calc'] = tmp[numeric_cols].sum(axis=1)
        proc_total = tmp.groupby('Process')['Total_calc'].agg(['mean', 'std', 'min', 'max']).reset_index()
        proc_total.columns = ['Process', 'Total_mean', 'Total_std', 'Total_min', 'Total_max']

    # 2) Component-level aggregated mean/std across simulations (sum across processes per sim, then compute mean/std)
    # For this, group by simulation and sum numeric columns across processes
    # Exclude the per-simulation 'Total' row added by conv_cost_to_df to avoid double-counting
    df_proc = df_all[df_all['Process'] != 'Total']
    comp_per_sim = df_proc.groupby('sim')[numeric_cols].sum()
    comp_stats = comp_per_sim.agg(['mean', 'std', 'min', 'max']).transpose().reset_index()
    # rename columns for clarity
    comp_stats.columns = ['Component', 'mean', 'std', 'min', 'max']

    return grouped, proc_total, comp_stats


def _print_progress(completed: int, total: int, bar_len: int = 40):
    """Print a simple progress bar to the terminal (overwrites the same line)."""
    if total <= 0:
        return
    completed = max(0, min(completed, total))
    frac = completed / total
    filled = int(round(frac * bar_len))
    bar = '#' * filled + '-' * (bar_len - filled)
    # \r to overwrite line; flush to ensure immediate update
    sys.stdout.write(f"\rProgress: |{bar}| {completed}/{total} sims")
    sys.stdout.flush()

def save_results_and_plots(proc_total, comp_stats, output_path: Path, filename_prefix: str, labels: Dict[str, str] = None, n_modules_mw: float = 1.0, round_vals: bool = True):
    """Create two waterfall charts (process-level and component-level) and save as PNGs.

    Waterfall:
    - Individual costs follow a constant, predefined order (missing items are skipped)
    - Bars stack cumulatively; Total bar is rightmost and spans 0 to total

    proc_total: DataFrame with columns ['Process', 'Total_mean', ...]
    comp_stats: DataFrame with columns ['Component', 'mean', ...]
    labels: optional dict to override axis/title labels; keys used below.
    n_modules_mw: multiplier to scale costs (mean values) for plotting
    round_vals: whether to round plotted values to nearest integer
    """
    labels = labels or {}
    output_path.mkdir(parents=True, exist_ok=True)

    # Fixed orders (deduplicate while preserving order; skip missing)
    proc_order_list = [
        'Injection Molding Plate',
        'Die Cutting IM Plate',
        'Die Cutting Film',
        'Laser Welding',
        'Gluing',
        'Assembly',
        'Injection Molding Header',
        'Injection Molding Plate',  # duplicate in spec; will be deduplicated
    ]
    # Deduplicate
    seen = set()
    PROCESS_ORDER = [p for p in proc_order_list if not (p in seen or seen.add(p))]

    COMPONENT_ORDER = [
        'Material', 'Equipment', 'Consumables', 'Labor', 'Facility', 'Utilities', 'Overhead'
    ]

    # ---------- Process-level waterfall ----------
    fig, ax = plt.subplots(figsize=(12, 6))
    proc_df = proc_total.copy()

    # Identify total row if present and separate contributions
    has_total_row = 'Process' in proc_df.columns and proc_df['Process'].eq('Total').any()
    total_mean = None
    if has_total_row:
        total_mean = float(proc_df.loc[proc_df['Process'] == 'Total', 'Total_mean'].iloc[0])
        proc_df = proc_df[proc_df['Process'] != 'Total']

    # Apply constant ordering to processes (append unexpected items at the end in their appearance order)
    existing_names = proc_df['Process'].astype(str).tolist()
    extras = [name for name in existing_names if name not in PROCESS_ORDER]
    extra_idx = {name: i for i, name in enumerate(extras)}

    def _proc_key(name: str) -> int:
        return PROCESS_ORDER.index(name) if name in PROCESS_ORDER else len(PROCESS_ORDER) + extra_idx.get(name, 0)

    proc_df['__order__'] = proc_df['Process'].apply(_proc_key)
    proc_df = proc_df.sort_values('__order__').drop(columns='__order__')

    contrib_names = proc_df['Process'].astype(str).tolist()
    contrib_vals = (proc_df['Total_mean'] * n_modules_mw).astype(float).tolist()

    if total_mean is None:
        total_mean = sum(contrib_vals) / (n_modules_mw if n_modules_mw else 1.0)  # unscaled base
    total_val_scaled = float(total_mean) * n_modules_mw

    if round_vals:
        contrib_vals = [int(round(v)) for v in contrib_vals]
        total_val_scaled = int(round(total_val_scaled))

    # Build cumulative bottoms for each contribution bar
    bottoms = []
    running = 0.0
    for v in contrib_vals:
        bottoms.append(running)
        running += v

    # X positions and labels: contributions + Total at rightmost
    x_positions = list(range(len(contrib_vals) + 1))
    x_labels = contrib_names + ['Total']

    # Plot contribution bars with bottom offsets (waterfall body)
    ax.bar(x_positions[:-1], contrib_vals, bottom=bottoms, color='tab:blue', alpha=0.8)
    # Plot total bar from 0 to total
    ax.bar(x_positions[-1], total_val_scaled, color='black', alpha=0.9)

    # Currency formatter
    currency_fmt = mticker.FuncFormatter(lambda x, pos: f'${x:,.0f}')

    # Data labels with currency
    for x, v, b in zip(x_positions[:-1], contrib_vals, bottoms):
        ax.text(x, b + v, f"${int(v):,}", ha='center', va='bottom')
    ax.text(x_positions[-1], total_val_scaled, f"${int(total_val_scaled):,}", ha='center', va='bottom', color='black')

    # Add percent-of-total labels in a straight horizontal line above bars (contributions only)
    y_max = max(sum(contrib_vals), total_val_scaled)
    if y_max <= 0:
        y_max = 1
    y_pct = y_max * 1.06
    for x, v in zip(x_positions[:-1], contrib_vals):
        pct = (v / total_val_scaled * 100.0) if total_val_scaled else 0.0
        ax.text(x, y_pct, f"{pct:.0f}%", ha='center', va='bottom', color='dimgray')
    # Ensure space for top labels
    ax.set_ylim(0, y_max * 1.2)

    ax.set_xticks(x_positions)
    ax.set_xticklabels(x_labels, rotation=45, ha='right')
    ax.set_xlabel(labels.get('proc_x', 'Process'))
    ax.set_ylabel(labels.get('proc_y', 'Cost ($/MW)'))
    ax.set_title(labels.get('proc_title', 'Cost Breakdown by Process Steps'))
    ax.yaxis.set_major_formatter(currency_fmt)
    plt.tight_layout()
    proc_plot_path = output_path / f"{filename_prefix}_proc_total.png"
    fig.savefig(proc_plot_path, dpi=200)
    plt.close(fig)

    # ---------- Component-level waterfall ----------
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    comp_df = comp_stats.copy()
    # Detect and extract Total row if present, then exclude it from contributions
    has_total_comp = 'Component' in comp_df.columns and comp_df['Component'].eq('Total').any()
    total_comp_scaled = None
    if has_total_comp:
        total_comp_scaled = float(comp_df.loc[comp_df['Component'] == 'Total', 'mean'].iloc[0]) * n_modules_mw
        comp_df = comp_df[comp_df['Component'] != 'Total']

    # Apply constant ordering to components (append unexpected items at the end)
    comp_names_exist = comp_df['Component'].astype(str).tolist()
    comp_extras = [c for c in comp_names_exist if c not in COMPONENT_ORDER]
    comp_extra_idx = {name: i for i, name in enumerate(comp_extras)}

    def _comp_key(name: str) -> int:
        return COMPONENT_ORDER.index(name) if name in COMPONENT_ORDER else len(COMPONENT_ORDER) + comp_extra_idx.get(name, 0)

    comp_df['__order__'] = comp_df['Component'].apply(_comp_key)
    comp_df = comp_df.sort_values('__order__').drop(columns='__order__')

    comp_names = comp_df['Component'].astype(str).tolist()
    comp_vals = (comp_df['mean'] * n_modules_mw).astype(float).tolist()
    # If no explicit total provided, compute it as sum of components
    if total_comp_scaled is None:
        total_comp_scaled = float(sum(comp_vals))

    if round_vals:
        comp_vals = [int(round(v)) for v in comp_vals]
        total_comp_scaled = int(round(total_comp_scaled))

    bottoms2 = []
    running2 = 0.0
    for v in comp_vals:
        bottoms2.append(running2)
        running2 += v

    x_positions2 = list(range(len(comp_vals) + 1))
    x_labels2 = comp_names + ['Total']

    ax2.bar(x_positions2[:-1], comp_vals, bottom=bottoms2, color='tab:orange', alpha=0.8)
    ax2.bar(x_positions2[-1], total_comp_scaled, color='black', alpha=0.9)

    # Data labels with currency
    for x, v, b in zip(x_positions2[:-1], comp_vals, bottoms2):
        ax2.text(x, b + v, f"${int(v):,}", ha='center', va='bottom')
    ax2.text(x_positions2[-1], total_comp_scaled, f"${int(total_comp_scaled):,}", ha='center', va='bottom', color='black')

    # Percent-of-total labels as a straight line above bars (components only)
    y_max2 = max(sum(comp_vals), total_comp_scaled)
    if y_max2 <= 0:
        y_max2 = 1
    y_pct2 = y_max2 * 1.06
    for x, v in zip(x_positions2[:-1], comp_vals):
        pct = (v / total_comp_scaled * 100.0) if total_comp_scaled else 0.0
        ax2.text(x, y_pct2, f"{pct:.0f}%", ha='center', va='bottom', color='dimgray')
    ax2.set_ylim(0, y_max2 * 1.2)

    ax2.set_xticks(x_positions2)
    ax2.set_xticklabels(x_labels2, rotation=45, ha='right')
    ax2.set_xlabel(labels.get('comp_x', 'Component'))
    ax2.set_ylabel(labels.get('comp_y', 'Cost ($/MW)'))
    ax2.set_title(labels.get('comp_title', 'Cost Breakdown by Manufacturing Inputs'))
    ax2.yaxis.set_major_formatter(currency_fmt)
    plt.tight_layout()
    comp_plot_path = output_path / f"{filename_prefix}_comp_stats.png"
    fig2.savefig(comp_plot_path, dpi=200)
    plt.close(fig2)

    return proc_plot_path, comp_plot_path

if __name__ == '__main__':
    # Quick CLI for convenience
    import argparse

    parser = argparse.ArgumentParser(description='Run Monte Carlo simulations for MPHX cost model')
    parser.add_argument('--scenario', choices=['mphx_sabic', 'mphx_oct24'], default='mphx_oct24')
    parser.add_argument('--join_method', default='Laser Welding')
    parser.add_argument('--ann_prod_vol', type=int, default=2074)
    parser.add_argument('--n_sim', type=int, default=100)
    parser.add_argument('--level', default='base')

    args = parser.parse_args()
    proc_by_metric, proc_total, comp_stats = monte_carlo_run(args.scenario, args.join_method, args.ann_prod_vol, args.n_sim, level=args.level)
    print('\nProcess-level metrics (mean/std) sample:')
    print(proc_by_metric.head())
    print('\nPer-process total cost mean/std:')
    print(proc_total)
    print('\nComponent-level aggregated mean/std:')
    print(comp_stats)
