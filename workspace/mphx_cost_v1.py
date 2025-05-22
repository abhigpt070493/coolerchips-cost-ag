# from copy import deepcopy
# from typing import Mapping
# import matplotlib.pyplot as plt

from analyses.Scenario import Scenario
from analyses.cost_output import calc_cost_obj, conv_cost_to_df
from analyses.iterations.mphx_oct24 import create_hx_oct24
from tools.color_scheme import set_color_scheme
from datetime import datetime
from tools.sensitivity_analysis import sensitivity_analysis_cont, sensitivity_analysis_disc

now = datetime.now()
formatted_now = now.strftime("%Y-%m-%d_%H-%M-%S")
output_path = "../workspace/outputs/"

if __name__ == "__main__":

    # ----- MODEL SET UP ----------------------------------------

    # set color palette for figures
    set_color_scheme('../input_data/vibrant_palette.json')

    # SCENARIO: EOS M290, with tolerance

    # initialize model from baseline
    model_hx, model_material, mfg_process, over, fac = create_hx_oct24()
    ann_prod_vol = 2074


    # set proposal_receiver baseline scenario
    baseline = Scenario(ann_prod_vol, model_hx, model_material, mfg_process, over, fac)

    #Set cost_functions unit
    cost_norm = ann_prod_vol

    # calculate cost_functions
    cost_bd_baseline = calc_cost_obj(baseline)

    df_base_cost = conv_cost_to_df(mfg_process, cost_bd_baseline)

    df_base_cost.to_csv(output_path + 'cost_bd_proc_' + str(formatted_now) + '.csv',index=False)

    # df_sensitivity = sensitivity_analysis(baseline,{"Injection Molding":["time_cycle", "batch_size"],"Laser Welding": ["time_cycle", "batch_size"]},[-20,20], 10)

    # df_sensitivity = sensitivity_analysis_disc(baseline, {"Injection Molding": {"time_cycle" :[], "batch_size": []},
    #                                                  "Laser Welding": {"time_cycle" : [], "batch_size" : []},
    #                                                   "Die Cutting IM Plate": {""}
    #                                                       })
    #
    # df_sensitivity.to_csv('/Users/abhishekgupta/Desktop/UM/T2M_Project/Model_outputs/cost_sensitivity_' + str(formatted_now) + '.csv',index=False)

