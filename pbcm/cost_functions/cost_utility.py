from pbcm.cost_items.Process import ProcessStep


def calc_util_cost(ann_prod_vol, mach_hrs_tot, elec_price, ps: ProcessStep) -> float:
    util_cost_tot = mach_hrs_tot * ps.mach.elec_consume_rate * elec_price
    util_cost_unit = util_cost_tot / ann_prod_vol

    return util_cost_unit
