from tools.monte_carlo import monte_carlo_run, save_results_and_plots
from datetime import datetime
from pathlib import Path


now = datetime.now()
formatted_now = now.strftime("%Y-%m-%d_%H-%M-%S")
# Construct output path robustly using pathlib
output_path = Path(__file__).parent / "outputs"

if __name__ == "__main__":
    # ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)

    # Run Monte Carlo for Laser Welding and save all three returned DataFrames
    proc_by_metric_lw, proc_total_lw, comp_stats_lw = monte_carlo_run(scenario_name='mphx_sabic', join_method="Laser Welding", ann_prod_vol=2074, n_sim=10000, level='base')
    proc_by_metric_lw.to_csv(output_path / f'proc_by_metric_{formatted_now}_lw.csv', index=False)
    proc_total_lw.to_csv(output_path / f'proc_total_{formatted_now}_lw.csv', index=False)
    comp_stats_lw.to_csv(output_path / f'comp_stats_{formatted_now}_lw.csv', index=False)
    # create and save plots for LW
    save_results_and_plots(proc_total_lw, comp_stats_lw, output_path, f'plots_{formatted_now}_lw', n_modules_mw=112)

    # Run Monte Carlo for Gluing and save all three returned DataFrames
    proc_by_metric_gl, proc_total_gl, comp_stats_gl = monte_carlo_run(scenario_name='mphx_sabic', join_method="Gluing", ann_prod_vol=2074, n_sim=10000, level='base')
    proc_by_metric_gl.to_csv(output_path / f'proc_by_metric_{formatted_now}_gl.csv', index=False)
    proc_total_gl.to_csv(output_path / f'proc_total_{formatted_now}_gl.csv', index=False)
    comp_stats_gl.to_csv(output_path / f'comp_stats_{formatted_now}_gl.csv', index=False)
    # create and save plots for Gluing
    save_results_and_plots(proc_total_gl, comp_stats_gl, output_path, f'plots_{formatted_now}_gl', n_modules_mw=112)
