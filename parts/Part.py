from copy import copy


class Part:
    """Describes Microchannel Polymer Heat Exchanger (MPHX) design."""

    def __init__(self, name, parent_part, mat_choice=None, wt=None, length=None, width=None, height=None, volume=0, count=1):
        """Initializes the parts with supplied design parameters"""
        self.name = name
        self.parent_part = parent_part
        self.mat_choice = mat_choice
        self.wt = wt
        self.length = length
        self.width = width
        self.height = height
        self.volume = volume
        self.count = count

    def add_subparts(self, subparts: dict):

        self.subs = {}
        for k, v in subparts.items():
            self.subs[k] = v
        return self

    def copy(self, **kwargs) -> "Part":
        res = copy(self)
        for k, v in kwargs:
            setattr(res, k, v)
        return res