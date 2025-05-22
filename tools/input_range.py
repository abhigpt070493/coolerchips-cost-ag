from copy import copy


class InputRange:

    def __init__(self, scenario_obj_type, distribution=None, upper=None, lower=None, mean=None, std_dev=None, best=None, rand=None):
        """
        Initializes an object to store information about input parameter distribution for use in uncertainty
        quantification.

        Parameters
        ----------
        scenario_obj_type: str
            Describes which scenario object hold the input value.

        upper: float or int, optional
            Upper bound value for input parameter.

        lower: float or int, optional
            Lower bound value for input parameter.

        mean: float or int, optional
            Mean value for input parameter.

        std_dev: float or int, optional
            Standard deviation for input parameter.

        best: float or int, optional
            Best estimate value for input parameter.

        rand: float, optional
            Stores random value drawn from distribution.
        """

        self.type = scenario_obj_type
        self.distribution = distribution
        self.upper = upper
        self.lower = lower
        self.mean = mean
        self.std_dev = std_dev
        self.best = best
        self.rand = rand

    def copy(self, **kwargs) -> "InputRange":
        """Creates a copy of the object, updates attributes for specified kwargs, and returns updated object."""

        res = copy(self)
        for k, v in kwargs.items():
            setattr(res, k, v)
        return res
