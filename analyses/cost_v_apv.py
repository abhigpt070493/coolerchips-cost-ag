import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from analyses import Scenario
from analyses.cost_output import calc_cost_obj
from tools.plot_format import format_axis_line


def calc_cost_v_apv(apv_min, apv_max, s: Scenario):
    """
    Calculates parts cost_functions at various annual production volumes (APV).

    Parameters
    ----------
    apv_min: int
        Smallest APV value.
    apv_max: int
        Largest APV value.
    s: Scenario
        An instance of Scenario class.
    Returns
    -------
    cost_v_apv: DataFrame
        Calculated unit, per kW, and per UA costs for each APV.
    """

    # Create an approximately 100 point log-spaced set of APV values between APV min and max values.
    #   Duplicate values removed.
    apv_range = np.unique(np.around(np.geomspace(apv_min, apv_max, 100)))
    data_apv = []

    # Calculate cost_functions for each APV value.
    for ann_prod_vol in apv_range:
        # Replace APV in Scenario
        dummy_scenario = s.copy(ann_prod_vol=ann_prod_vol)
        # Calculate cost_functions at new APV
        cost_bd = calc_cost_obj(dummy_scenario)
        data_apv.append([ann_prod_vol, cost_bd.cost_kw, cost_bd.cost_ua, cost_bd.cost_unit])

    # Store calculation results in pandas DataFrame.
    cost_v_apv = pd.DataFrame(data_apv, columns=["Annual Production Volume", "Cost/kW-th", "Cost/UA", "Cost/unit"])

    return cost_v_apv


def plot_cost_v_apv(cost_v_apv, filepath: str, units="Cost/kW-th"):
    """
    Plots cost_functions in $/kW vs. annual production volume (APV).

    Parameters
    ----------
    units
    cost_v_apv: DataFrama
        DataFrame containing APVs and costs at each APV.
    filepath: str
        Specifies the filename and location for .png of plot.

    -------

    """
    cost_norm = units

    _, g = plt.subplots()
    g = sns.relplot(x="Annual Production Volume", y=cost_norm, kind="line", data=cost_v_apv, linewidth=3.5)
    g.set(xlim=(10, 10000), xscale='log')
    g = format_axis_line(g, xtext='{:,.0f}', ytext='$' + '{:,.0f}')
    axins = inset_axes(g.axes[0][0], "65%", "50%", loc="upper right")
    sns.lineplot(x="Annual Production Volume", y=cost_norm, data=cost_v_apv, linewidth=3.5, ax=axins)
    axins.set(xlim=(10, 1000), xscale='log')
    xticks = axins.get_xticks()
    xlabels = ['{:,.0f}'.format(x) for x in xticks]
    axins.set(xticklabels=xlabels, xlabel="")
    axins.set(ylim=(0, 3500), yscale="linear")
    yticks = axins.get_yticks()
    ylabels = ['$' + '{:,.0f}'.format(y) for y in yticks]
    axins.set(yticklabels=ylabels, ylabel="")
    g.savefig(filepath)
    return
