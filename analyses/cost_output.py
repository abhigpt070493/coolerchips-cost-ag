from analyses import Scenario
from parts.Mphx import Mphx
from pbcm.cost_items.Facility import Facility
from pbcm.cost_items.Material import Material
from pbcm.cost_items.Overhead import Overhead
from pbcm.cost_functions.Cost_Breakdown import CostBreakdown
from pbcm.cost_functions.dist_overhead import distribute_overhead
from pbcm.cost_functions.cost_consumables import calc_consume_cost
from pbcm.cost_functions.cost_equipment import calc_mach_count, calc_equip_cost
from pbcm.cost_functions.cost_facility import calc_fac_size, calc_fac_cost
from pbcm.cost_functions.cost_labor import calc_n_labor, calc_labor_cost
from pbcm.cost_functions.cost_material import calc_mat_cost
from pbcm.cost_functions.cost_overhead import calc_overhead_cost_alt
from pbcm.cost_functions.cost_utility import calc_util_cost
from pbcm.cost_items.epv import calc_eff_prod_vol
import pandas as pd
import ast


def calc_cost(ann_prod_vol, mfg_process, model_mat: Material, model_hx: Mphx, over: Overhead, fac: Facility):
    eff_prod_vol = calc_eff_prod_vol(ann_prod_vol, mfg_process)

    mat_cost_unit = calc_mat_cost(ann_prod_vol,
                                  eff_prod_vol,
                                  model_mat, model_hx,
                                  fac.printer_scrap_frac,
                                  fac.int_powder_recover_frac)
    tot_equip_cost_unit = 0
    tot_labor_cost_unit = 0
    tot_util_cost_unit = 0
    tot_fac_cost_unit = 0
    tot_consume_cost_unit = 0
    n_labor_tot = 0
    fac_size_tot = 0
    proc_cost_bd = {}

    for k, v in mfg_process.items():

        print("Calculating cost for "+str(k))
        n_mach, mach_hrs_tot, eff_part_vol = calc_mach_count(fac.dedicate_equip, eff_prod_vol, fac.ann_ops_hrs, v, model_hx)
        print("No. of machines = "+ str(n_mach))
        print("Machine operating hours = " + str(mach_hrs_tot))
        print("Effective part volume = " + str(eff_part_vol))
        print("\n")

        equip_cost_proc = calc_equip_cost(fac.ann_ops_hrs, ann_prod_vol, n_mach, fac.discount_rate, v)

        consume_cost_proc = calc_consume_cost(ann_prod_vol, eff_part_vol, mach_hrs_tot, v)

        n_labor = calc_n_labor(n_mach, fac.dedicate_labor, eff_prod_vol, fac.ann_ops_hrs, fac.ann_labor_hrs, v)
        labor_cost_proc = calc_labor_cost(ann_prod_vol, fac.salary, fac.labor_burden, n_labor)

        fac_size = calc_fac_size(n_mach, v)
        fac_cost_proc = calc_fac_cost(ann_prod_vol, fac_size, fac)

        util_cost_proc = calc_util_cost(ann_prod_vol, mach_hrs_tot, fac.elec_price, v)

        proc_cost_total = equip_cost_proc + labor_cost_proc + fac_cost_proc + util_cost_proc + consume_cost_proc
        fac_config = {'n_mach': n_mach, 'mach_hrs_tot': mach_hrs_tot, 'n_labor': n_labor, 'fac_size': fac_size}
        v.add_fac_config(fac_config)
        proc_cost = {'total': proc_cost_total, 'equip': equip_cost_proc, 'labor': labor_cost_proc, 'fac': fac_cost_proc,
                     'util': util_cost_proc, 'consume': consume_cost_proc}
        v.add_proc_cost(proc_cost)
        proc_cost_bd[v.name_process_step] = proc_cost_total

        tot_equip_cost_unit = tot_equip_cost_unit + equip_cost_proc
        tot_labor_cost_unit = tot_labor_cost_unit + labor_cost_proc
        tot_util_cost_unit = tot_util_cost_unit + util_cost_proc
        tot_fac_cost_unit = tot_fac_cost_unit + fac_cost_proc
        tot_consume_cost_unit = tot_consume_cost_unit + consume_cost_proc
        n_labor_tot = n_labor_tot + n_labor
        fac_size_tot = fac_size_tot + fac_size

    overhead_cost_unit = calc_overhead_cost_alt(over, model_hx, n_labor_tot, eff_prod_vol, fac.ann_labor_hrs,
                                                ann_prod_vol, fac.fac_rent, fac_size_tot, fac.discount_rate, fac.salary)

    # tot_cost_unit = sum(proc_cost_bd.values())
    # overhead_cost_unit = calc_overhead_cost(tot_cost_unit, fac.overhead_frac)

    proc_cost_bd = distribute_overhead(proc_cost_bd, overhead_cost_unit, mfg_process)

    cost_bd = CostBreakdown()
    cost_bd.add_cost_cat(mat_cost_unit, tot_equip_cost_unit, tot_labor_cost_unit, tot_util_cost_unit, tot_fac_cost_unit,
                         overhead_cost_unit, tot_consume_cost_unit)

    cost_bd.add_proc_cost(proc_cost_bd)
    cost_unit = mat_cost_unit + tot_equip_cost_unit + tot_labor_cost_unit + overhead_cost_unit + tot_util_cost_unit + tot_fac_cost_unit + tot_consume_cost_unit

    # model_hx.calc_rating_kw()
    # cost_kw = cost_unit / model_hx.rating_kw
    # cost_ua = cost_unit / model_hx.rating_ua

    # cost_kw = cost_unit
    # cost_ua = cost_unit
    # cost_bd.add_cost_total(cost_unit, cost_ua, cost_kw)

    cost_bd.add_cost_total(cost_unit,0,0)

    return cost_bd


def calc_cost_obj(s: Scenario):
    cost_bd = calc_cost(s.ann_prod_vol, s.mfg_process, s.model_material, s.model_hx, s.over, s.fac)
    return cost_bd

def conv_cost_to_df(mfg_process, cost_bd):

    # Creating dataframe to export results to csv
    df_cost=pd.DataFrame()
    for i, j in mfg_process.items():
        data = ast.literal_eval(str(j.proc_cost))
        data.update({"Process": i})
        data = {key: [value] for key, value in data.items()}
        df_temp = pd.DataFrame.from_dict(data)
        df_cost = pd.concat([df_cost, df_temp], ignore_index=True)
        print(i + " : " + str(j.proc_cost))

    df_cost = df_cost[["Process","equip","labor","fac","util","consume","overhead","total"]]
    df_cost = df_cost.rename(columns={"equip":"Equipment", "labor":"Labor", "fac":"Facility", "util":"Utilities", "consume":"Consumables", "overhead":"Overhead", "total":"Total"})
    df_cost.loc[len(df_cost)] = ["Material", 0, 0, 0, 0, 0, 0, cost_bd.mat_cost]
    column_totals = df_cost.sum(numeric_only=True)
    totals_df = pd.DataFrame(column_totals).T
    totals_df ["Process"] = ["Total"]
    last_column = totals_df.iloc[:, -1]
    totals_df.drop(totals_df.columns[-1], axis=1, inplace=True)
    totals_df.insert(0, last_column.name, last_column)
    df_cost = pd.concat([df_cost, totals_df])

    return df_cost