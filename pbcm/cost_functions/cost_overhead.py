import math

from pbcm.cost_functions.capital_recovery_factor import calc_crf
from pbcm.cost_items.Overhead import Overhead
from parts.Mphx import Mphx
# from parts.Socket import Socket
# from parts.Pipe import Pipe


def calc_overhead_cost(tot_labor_cost_unit, overhead_frac) -> float:
    overhead_cost_unit = tot_labor_cost_unit * overhead_frac
    return overhead_cost_unit


def calc_overhead_cost_alt(over: Overhead, hx: Mphx, n_labor, eff_prod_vol, ann_labor_hrs, ann_prod_vol, fac_rent,
                           fac_size, discount_rate, salary):
    # unused mfg labor
    n_labor_unused = math.ceil(n_labor) - n_labor
    cost_unused_labor = salary * n_labor_unused

    # management
    n_mgmt = over.mgmt_ratio * n_labor
    cost_mgmt = n_mgmt * over.mgmt_salary

    # quality assurance
    n_qa_parts = math.ceil(over.qa_inspect_frac * eff_prod_vol)
    n_qa_labor = n_qa_parts * over.qa_time / ann_labor_hrs
    cost_qa = n_qa_labor * over.qa_salary

    # administrative staff
    n_admin = n_labor * over.admin_ratio
    admin_cost = n_admin * over.admin_salary

    # human resources
    n_employee = n_labor + n_qa_labor + n_mgmt + n_admin
    hr_cost = n_employee * over.hr_price

    # compliance
    cp_cost = over.cp_cost * n_employee

    # legal
    legal_hr = ann_prod_vol * over.legal_frac
    legal_cost = legal_hr * 12 * over.legal_price

    # insurance
    insure_cost = over.insure_price

    # accounting
    acct_cost = 12 * over.acct_price

    # office space
    n_office_employee = n_admin + n_mgmt + n_qa_labor
    office_space = over.space_emp * n_office_employee
    office_build_crf = calc_crf(discount_rate, over.office_life)
    furn_cost = office_build_crf * over.office_build_price * n_office_employee #why n_office here?


    # inventory space
    n_inventory = ann_prod_vol / 365 * over.inventory_time
    if hx.height == 0:
        inventory_space = 0
    else:
        n_m2 = (over.inventory_stack_height / hx.height) * 1 / (hx.width * hx.length)
        inventory_space = n_inventory / n_m2

    # misc space (packaging, qa, supplies, etc)
    misc_space = over.misc_space_frac * (office_space + inventory_space + fac_size)

    # overhead space cost_functions
    overhead_space = office_space + inventory_space + misc_space
    space_cost = fac_rent * overhead_space + furn_cost

    tot_space = overhead_space + fac_size

    # cleaning
    cleaning_cost = 12 * over.clean_price * tot_space

    # office supplies
    cost_supplies = n_employee * over.supply_price

    # IT equipment
    cost_it = n_employee * over.it_price

    # packaging
    pack_cost = over.crate_price * ann_prod_vol

    # general building utilities
    building_util_cost = over.building_util * (overhead_space + fac_size)

    # print("Overhead breakdown\n"+"cost_unused_labor: "+str(cost_unused_labor)+"\n"+"cost_mgmt: "+str(cost_mgmt)+"\n"+"cost_qa: "+str(cost_qa)+"\n"+"cp_cost: "+str(cp_cost)+"\n"+"legal_cost: "+str(legal_cost)+"\n"+"insure_cost: "+str(insure_cost)+"\n"+"hr_cost: "+str(hr_cost)+"\n"+"admin_cost: "+str(admin_cost)+"\n"+"acct_cost: "+str(acct_cost)+"\n"+"space_cost: "+str(space_cost)+"\n"+"cleaning_cost: "+str(cleaning_cost)+"\n"+"cost_supplies: "+str(cost_supplies)+"\n"+"cost_it: "+str(cost_it)+"\n"+"pack_cost: "+str(pack_cost)+"\n"+"building_util_cost: "+str(building_util_cost)+"\n")

    # total overhead cost_functions
    overhead_cost_tot = cost_unused_labor + cost_mgmt + cost_qa + cp_cost + legal_cost + insure_cost + hr_cost + admin_cost + acct_cost + space_cost + cleaning_cost + cost_supplies + cost_it + pack_cost + building_util_cost
    overhead_cost_unit = overhead_cost_tot / ann_prod_vol
    return overhead_cost_unit