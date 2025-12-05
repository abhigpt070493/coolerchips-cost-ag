import math

from pbcm.cost_functions.capital_recovery_factor import calc_crf
from pbcm.cost_items.Process import ProcessStep
from parts.Part import Part


def calc_mach_count(dedicate_mach: bool, eff_prod_vol, ann_ops_hrs,
                    ps: ProcessStep, hx: Part):
    mach_hrs_batch = ps.time_cycle + ps.mach.time_setup + ps.mach.time_teardown + ps.mach.time_heat + ps.mach.time_cool
    mach_hrs_unit = mach_hrs_batch*1.00/ps.batch_size
    ann_part_vol = ann_ops_hrs*1.00/mach_hrs_unit


    eff_part_vol = eff_prod_vol * ps.parts_per_unit

    mach_hrs_tot = eff_part_vol * mach_hrs_unit

    n_mach = 0
    if dedicate_mach:
        n_mach = math.ceil(eff_part_vol / ann_part_vol)
    else:
        n_mach = eff_part_vol / ann_part_vol

    return n_mach, mach_hrs_tot, eff_part_vol


def calc_equip_cost(ann_ops_hrs, ann_prod_vol, n_mach, discount_rate, ps: ProcessStep) -> float:
    mach_hrs_batch = ps.time_cycle + ps.mach.time_setup + ps.mach.time_teardown + ps.mach.time_heat + ps.mach.time_cool
    mach_hrs_unit = mach_hrs_batch*1.00/ps.batch_size
    ann_prod_plate = ann_ops_hrs*1.00/mach_hrs_unit

    if ps.mach.mach_life_unit == "years":
        mach_life =  ps.mach.mach_life
    elif ps.mach.mach_life_unit == "parts":
        mach_life = ps.mach.mach_life/ann_prod_plate
    mach_crf = calc_crf(discount_rate, mach_life)

    # Helper to interpret cost values: accepts absolute numbers, fractional percentages (0 < v < 1),
    # or percentage strings like '10%'. If a percentage is provided, it is applied to price_mach.
    def _resolve_cost(value, base):
        if value is None:
            return 0.0
        # Strings like '10%'
        if isinstance(value, str):
            v = value.strip()
            if v.endswith('%'):
                try:
                    return float(v[:-1]) / 100.0 * base
                except Exception:
                    return 0.0
            try:
                return float(v)
            except Exception:
                return 0.0
        try:
            fv = float(value)
        except Exception:
            return 0.0
        # Treat fractional values between 0 and 1 as percentages of base
        if 0 < fv < 1:
            return fv * base
        # Otherwise treat as absolute
        return fv

    inst_cost_val = _resolve_cost(getattr(ps.mach, 'cost_inst', 0.0), ps.mach.price_mach)
    maint_cost_val = _resolve_cost(getattr(ps.mach, 'cost_maint', 0.0), ps.mach.price_mach)

    mach_cost_ann = mach_crf * (
            ps.mach.price_mach + inst_cost_val) + maint_cost_val

    equip_cost_tot = n_mach * mach_cost_ann
    equip_cost_unit = equip_cost_tot / ann_prod_vol

    return equip_cost_unit
