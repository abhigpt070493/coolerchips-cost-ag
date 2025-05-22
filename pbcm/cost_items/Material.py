from copy import copy


class Material:

    def __init__(self, name_mat, density, price_mat, raw=None):
        """
         Initializes an object to hold attributes of a material used in fabrication of parts.

        Parameters
        ----------
        name_mat: str
            Name of a material that will be incorporated into the parts during fabrication.

        density: float or int
            Density (kg/m^3) of the material.

        price_mat: float or int
            Unit price ($/kg) of the material.

        raw: dict
            Dictionary of raw data for objects created from an external data file.

        Notes
        _____
        The Material class only capture materials that are incorporated into the parts during the fabrication process.
        Materials or items used incidentally in the fabrication process are captured by the Consumable class.

        """
        self.name_mat = name_mat
        self.density = density
        self.price_mat = price_mat
        self.raw = raw

    def copy(self, **kwargs) -> "Material":
        """Creates a copy of the object, updates attributes for specified kwargs, and returns updated object."""

        res = copy(self)
        for k, v in kwargs:
            setattr(res, k, v)
        return res
