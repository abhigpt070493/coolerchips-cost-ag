from copy import copy


class Facility:

    def __init__(self, ann_ops_hrs, ann_labor_hrs, elec_price, fac_rent, discount_rate, labor_burden,
                 overhead_frac, salary, dedicate_equip, dedicate_labor, int_powder_recover_frac=0, printer_scrap_frac=0, fac_buildout=0, raw=None):
        # Facility Hours
        self.ann_ops_hrs = ann_ops_hrs
        self.ann_labor_hrs = ann_labor_hrs

        # Utility Prices
        self.elec_price = elec_price

        # Facility Prices
        self.fac_rent = fac_rent
        self.fac_buildout = fac_buildout

        # Financials
        self.discount_rate = discount_rate
        self.labor_burden = labor_burden
        self.overhead_frac = overhead_frac
        self.salary = salary

        # material scrap/recycling
        self.printer_scrap_frac = printer_scrap_frac
        self.int_powder_recover_frac = int_powder_recover_frac

        # Dedication
        self.dedicate_equip = dedicate_equip
        self.dedicate_labor = dedicate_labor

        self.raw = raw

    def copy(self, **kwargs) -> "Facility":
        res = copy(self)
        for k, v in kwargs.items():
            setattr(res, k, v)
        return res
