import math

from pbcm.cost_items.Process import ProcessStep

def calc_n_labor(n_mach,dedicate_labor: bool, eff_prod_vol, ann_ops_hrs, ann_labor_hrs, ps: ProcessStep):
    labor_hrs_tot = (ann_ops_hrs * ps.mach.laborfrac_cycle * n_mach)
    # labor_hrs_batch = ps.time_cycle * ps.mach.laborfrac_cycle + ps.mach.time_setup * ps.mach.laborfrac_setup + ps.mach.time_teardown * ps.mach.laborfrac_teardown + ps.mach.time_heat * ps.mach.laborfrac_heat + ps.mach.time_cool * ps.mach.laborfrac_cool
    # labor_hrs_tot = eff_prod_vol * labor_hrs_batch

    if dedicate_labor:
        n_labor = math.ceil(labor_hrs_tot / ann_labor_hrs)
    else:
        n_labor = labor_hrs_tot / ann_labor_hrs

    return n_labor

# def calc_n_labor(dedicate_labor: bool, eff_prod_vol, ann_labor_hrs, ps: ProcessStep):
#     labor_hrs_batch = ps.time_cycle * ps.mach.laborfrac_cycle + ps.mach.time_setup * ps.mach.laborfrac_setup + ps.mach.time_teardown * ps.mach.laborfrac_teardown + ps.mach.time_heat * ps.mach.laborfrac_heat + ps.mach.time_cool * ps.mach.laborfrac_cool
#     labor_hrs_tot = eff_prod_vol * labor_hrs_batch
#
#     if dedicate_labor:
#         n_labor = math.ceil(labor_hrs_tot / ann_labor_hrs)
#     else:
#         n_labor = labor_hrs_tot / ann_labor_hrs
#
#     return n_labor


def calc_labor_cost(ann_prod_vol, salary, labor_burden, n_labor):
    labor_cost_tot = n_labor * salary * (1 + labor_burden)
    labor_cost_unit = labor_cost_tot / ann_prod_vol

    return labor_cost_unit
