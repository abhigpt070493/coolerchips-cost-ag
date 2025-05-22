from copy import copy


class CostBreakdown:
    """"""

    def __init__(self):
        """Initializes the material with supplied name, density, and price."""

        self.cost_unit = 0
        self.cost_ua = 0
        self.cost_kw = 0
        self.mat_cost = 0
        self.equip_cost = 0
        self.labor_cost = 0
        self.overhead_cost = 0
        self.util_cost = 0
        self.fac_cost = 0
        self.fac_cost = 0
        self.consume_cost = 0
        self.proc_cost = {}

    def copy(self, **kwargs) -> "CostBreakdown":
        res = copy(self)
        for k, v in kwargs.items():
            setattr(res, k, v)
        return res

    def add_cost_cat(self, mat_cost_unit, tot_equip_cost_unit, tot_labor_cost_unit, tot_util_cost_unit,
                     tot_fac_cost_unit, overhead_cost_unit, consume_cost_unit):
        """

        Parameters
        ----------
        mat_cost_unit
        tot_equip_cost_unit
        tot_labor_cost_unit
        tot_util_cost_unit
        tot_fac_cost_unit
        overhead_cost_unit
        consume_cost_unit

        Returns
        -------

        """
        self.mat_cost = mat_cost_unit
        self.equip_cost = tot_equip_cost_unit
        self.labor_cost = tot_labor_cost_unit
        self.overhead_cost = overhead_cost_unit
        self.util_cost = tot_util_cost_unit
        self.fac_cost = tot_fac_cost_unit
        self.consume_cost = consume_cost_unit

    def add_cost_total(self, cost_unit, cost_ua, cost_kw):
        self.cost_unit = cost_unit
        self.cost_ua = cost_ua
        self.cost_kw = cost_kw

    def add_proc_cost(self, proc_cost):
        self.proc_cost = proc_cost
