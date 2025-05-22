from copy import copy


class Mphx:
    """Describes Microchannel Polymer Heat Exchanger (MPHX) design."""

    def __init__(self, name_hx, mat_choice, wt_plate=None, length=None, width=None, height=None,
                 n_pins=None, n_fins=None, n_plates=None):
        """Initializes the parts with supplied design parameters

        Parameters
        ----------
        n_pins
        n_fins
        n_plates
        """
        self.name_hx = name_hx
        self.mat_choice = mat_choice
        self.wt_plate = wt_plate
        self.length = length
        self.width = width
        self.height = height
        self.volume = 0
        self.n_pins = n_pins
        self.n_fins = n_fins
        self.n_plates = n_plates

    def add_subparts(self, subparts):
        self.subs = subparts

    def copy(self, **kwargs) -> "Mphx":
        res = copy(self)
        for k, v in kwargs:
            setattr(res, k, v)
        return res