from copy import copy


class Consumable:

    def __init__(self, name_mach, name, consume_price, price_unit, consume_life, life_unit, brand=None, raw=None):
        """
        Initializes an object to hold attributes of a consumable tool, material, or similar used during operation of
        a machine.

        Parameters
        ----------
        name_mach: str
            Name of the machine with which the consumable is used. This str MUST
            exactly equal the "name_mach" str for the associated Machine object.

        name: str
            Name of the consumable.

        consume_price: float or int
            Price of the consumable per unit.

        price_unit: str
            Units for consume_price (e.g. $/piece).

        consume_life: float or int
            Amount of consumable used (or replacement frequency) per period of time, per parts, or per machine.

        life_unit: str
            Units for consume_life. Options recognized by cost_consumables function are "hrs" and "unit".

        brand: str, optional
            Manufacturer of the machine.

        raw: dict
            Dictionary of raw data for objects created from an external data file.
        """

        self.name_mach = name_mach
        self.name = name
        self.consume_price = consume_price
        self.price_unit = price_unit
        self.consume_life = consume_life
        self.life_unit = life_unit
        self.brand = brand
        self.raw = raw

    def copy(self, **kwargs) -> "Consumable":
        """Creates a copy of the object, updates attributes for specified kwargs, and returns updated object."""

        res = copy(self)
        for k, v in kwargs.items():
            setattr(res, k, v)
        return res
