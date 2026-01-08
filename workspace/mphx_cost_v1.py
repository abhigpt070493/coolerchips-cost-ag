# from copy import deepcopy
# from typing import Mapping
# import matplotlib.pyplot as plt

import sys
from pathlib import Path

# Ensure project root is on sys.path so that 'analyses', 'tools', etc. can be imported
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analyses.Scenario import Scenario
from analyses.cost_output import calc_cost_obj, conv_cost_to_df
# from analyses.iterations.mphx_oct24 import create_hx
from analyses.iterations.mphx_sabic import create_hx
from tools.color_scheme import set_color_scheme
from datetime import datetime

now = datetime.now()
formatted_now = now.strftime("%Y-%m-%d_%H-%M-%S")
# Construct output path robustly using pathlib
output_path = Path(__file__).parent / "outputs"

if __name__ == "__main__":

    # ----- MODEL SET UP ----------------------------------------

    # SCENARIO: EOS M290, with tolerance

    # initialize model from baseline
    model_hx, mfg_process, over, fac = create_hx(join_method="Gluing", level='base')
    ann_prod_vol = 2074


    # set proposal_receiver baseline scenario
    baseline = Scenario(ann_prod_vol, model_hx, mfg_process, over, fac)

    #Set cost_functions unit
    cost_norm = ann_prod_vol

    # calculate cost_functions
    cost_bd_baseline = calc_cost_obj(baseline)

    df_base_cost = conv_cost_to_df(mfg_process, cost_bd_baseline)

    # Save CSV using robust path
    df_base_cost.to_csv(output_path / f'cost_bd_proc_{formatted_now}.csv', index=False)
