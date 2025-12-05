import math

import numpy as np


def calc_eff_prod_vol(apv, proc: dict) -> float:
    """This function calcs the effective annual production volume, EPV using the input_data:
        APV - Annual Production Volume, the number of units produced each year
        process_steps - definition of the full manufacturing process as a list of ProcessStep objects
        
        EPV is calculated as the APV divided by the product of the parts acceptance rates for each process step.
    """
    part_accept = []
    for k, v in proc.items():
        part_accept.append(v.mach.part_accept_rate)
    eff_prod_vol = math.ceil(apv / np.prod(part_accept))
    return eff_prod_vol