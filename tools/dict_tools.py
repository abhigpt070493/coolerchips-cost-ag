import inspect
from copy import deepcopy


def select_level(d, level):
    """
        Creates a single level dict from a specified level in a multi-level dict

        Parameters
        ----------
        d: dict
            Multi-level dict from which function will create single level dict
        level: str

            Specifies level of dict to use for single level dict

        Returns
        -------
        dl: dict
            Single level dict from level specified in function input
        flattened: bool
            Indicator of whether an values in dl were flattened from multi-level dict
        """
    dl = deepcopy(d)
    flattened = False
    for k, v in dl.items():
        if type(v) is dict:
            dl[k] = v[level]
            flattened = True
    return dl, flattened


def from_dict(clazz, d, level='base'):
    """
    Creates an instance of a class from parameters stored in dict

    Parameters
    ----------
    clazz: Class
        Class of which function will create an instance
    d: dict
        Dict containing parameters for function
    level: str
        For multi-level dict, specifies level of dict to use for Class instance

    Returns
    -------
    clazz: Class
        Instance of clazz

    """
    df, flattened = select_level(d, level)
    allowed = dict(inspect.signature(clazz.__init__).parameters)
    df2 = {k: v for k, v in iter(df.items()) if k in allowed}
    if flattened:
        return clazz(**df2)
    else:
        return clazz(**df2)

