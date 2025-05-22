from pbcm.cost_items.Facility import Facility
from pbcm.cost_items.Process import ProcessStep
from pbcm.cost_functions.capital_recovery_factor import calc_crf


def calc_fac_size(n_mach, ps: ProcessStep) -> float:
    fac_size = n_mach * (ps.mach.area_floor_space + ps.mach.area_clearance)

    return fac_size


def calc_fac_cost(ann_prod_vol, fac_size, fac:Facility=None) -> float:


    fac_crf = calc_crf(fac.discount_rate, 20)
    discount_fac_buildout = fac_crf*fac.fac_buildout
    fac_cost_tot = fac_size * (fac.fac_rent + discount_fac_buildout)
    fac_cost_unit = fac_cost_tot / ann_prod_vol

    return fac_cost_unit
