import pandas as pd
import matplotlib.pyplot as plt

from analyses import Scenario
from analyses.cost_output import calc_cost_obj
from tools.plot_format import format_stackbar


def calc_proc_cat(apv_details, s: Scenario, units="Cost/kW-th"):
    if units == "unit":
        cost_norm = 1
    elif units == "Cost/kW-th":
        cost_norm = s.model_hx.rating_kw
    elif units == "Cost/UA":
        cost_norm = s.model_hx.rating_ua
    else:
        cost_norm = 1


    # Breakdown by cost_functions category & subprocess
    data_cat = []
    data_cat_am = []
    data_proc = []

    for ann_prod_vol in apv_details:
        dummy_scenario = s.copy(ann_prod_vol=ann_prod_vol)
        cost_bd = calc_cost_obj(dummy_scenario)

        # Cost breakdown by category
        data_cat.append([ann_prod_vol, cost_bd.equip_cost, cost_bd.mat_cost, cost_bd.labor_cost, cost_bd.fac_cost,
                         cost_bd.util_cost, cost_bd.overhead_cost, cost_bd.consume_cost])

        # Cost breakdown by subprocess
        data = [ann_prod_vol, cost_bd.mat_cost]
        for k, v in cost_bd.proc_cost.items():
            data.append(v)
        data_proc.append(data)

        # Hybrid cost_functions breakdown (AM by category, material, combined remaining subprocess costs)
        post_proc_cost = 0
        for k, v in s.mfg_process.items():
            if k == "3D Printing (LPBF)":
                post_proc_cost = post_proc_cost
            else:
                post_proc_cost = post_proc_cost + v.proc_cost["total"]
        data = [ann_prod_vol, cost_bd.mat_cost, post_proc_cost]
        for k, v in s.mfg_process["3D Printing (LPBF)"].proc_cost.items():
            if k == "total":
                continue
            else:
                data.append(v)
        data_cat_am.append(data)

    # Cost by cat Dataframe
    cost_cat = pd.DataFrame(data_cat,
                            columns=["APV", "Equipment", "Material", "Labor", "Facility", "Utilities", "Overhead",
                                     "Consumables"], index=apv_details)
    cost_cat = cost_cat[["APV", "Equipment", "Material", "Labor", "Facility", "Consumables", "Utilities", "Overhead"]]

    for i in ["Equipment", "Material", "Labor", "Facility", "Utilities", "Overhead",
              "Consumables"]:
        cost_cat[i] = cost_cat[i] / cost_norm

    # Cost by proc Dataframe
    cost_proc = pd.DataFrame(data_proc, columns=["APV", "Material", "parts Printing (AM DLMS)", "Stress Relief Heat Treat",
                                                 "Baseplate & Support Removal (CNC)",
                                                 "Internal Passage Cleaning (AFM)"])

    for i in ["Material", "parts Printing (AM DLMS)", "Stress Relief Heat Treat", "Baseplate & Support Removal (CNC)",
              "Internal Passage Cleaning (AFM)"]:
        cost_proc[i] = cost_proc[i] / cost_norm
    cost_proc = cost_proc[["parts Printing (AM DLMS)", "Material", "Baseplate & Support Removal (CNC)",
                           "Internal Passage Cleaning (AFM)", "Stress Relief Heat Treat"]]

    # Hybrid cost_functions Dataframe
    cost_cat_am = pd.DataFrame(data_cat_am,
                               columns=["APV", "Material", "Post Processing", "AM Equipment", "AM Labor",
                                        "AM Facility", "AM Utilities", "AM Consumables", "AM Overhead"]
                               )
    cost_cat_am = cost_cat_am[
        ["APV", "Material", "Post Processing", "AM Equipment", "AM Labor", "AM Facility", "AM Consumables",
         "AM Utilities", "AM Overhead"]]

    for i in ["Material", "Post Processing", "AM Equipment", "AM Labor", "AM Facility", "AM Consumables",
              "AM Utilities", "AM Overhead"]:
        cost_cat_am[i] = cost_cat_am[i] / cost_norm

    return cost_cat, cost_cat_am, cost_proc


def plot_proc_cat(apv_details, data: pd.DataFrame, filename: str):
    g = data.plot.bar(stacked=True, width=0.65, edgecolor="white", linewidth=0.3)
    ymin, ymax = plt.gca().get_ylim()
    plt.ylim(min(ymin, 0), max(ymax, 0))
    g = format_stackbar(g, apv_details, " ")
    g.figure.set_tight_layout("pad")
    g.figure.savefig(filename, dpi=300)
    return g
