from pbcm.cost_items.Process import ProcessStep


def calc_consume_cost(ann_prod_vol, eff_part_vol, mach_hrs_tot, proc: ProcessStep, batch=5) -> float:
    consume_cost_tot = 0
    consumes = proc.mach.consume_list
    for k, v in consumes.items():
        if v.life_unit == "hrs" or v.life_unit == "hr":
            n_consumes = mach_hrs_tot / v.consume_life
        elif v.life_unit == "parts" or v.life_unit == "parts":
            n_consumes = eff_part_vol / v.consume_life
        else:
            n_consumes = 0
        # if proc.name_process_step == "3D Printing (LPBF)":
        #     n_consumes = n_consumes/batch
        # else:
        #     n_consumes = n_consumes
        consume_cost_ind = n_consumes * v.consume_price
        consume_cost_tot = consume_cost_tot + consume_cost_ind
    consume_cost_unit = consume_cost_tot / ann_prod_vol
    return consume_cost_unit
