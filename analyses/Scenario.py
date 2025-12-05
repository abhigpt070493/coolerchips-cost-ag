from copy import copy


class Scenario:

    def __init__(self, ann_prod_vol, model_hx, mfg_process, over, fac, print_settings=None):
        self.ann_prod_vol = copy(ann_prod_vol)
        self.model_hx = copy(model_hx)
        self.mfg_process = copy(mfg_process)
        self.over = copy(over)
        self.fac = copy(fac)
        self.print_settings = copy(print_settings)

    def copy(self, **kwargs) -> "Scenario":
        """Creates a copy of the object, updates attributes for specified kwargs, and returns updated object."""

        res = copy(self)
        for k, v in kwargs.items():
            setattr(res, k, v)
        return res
