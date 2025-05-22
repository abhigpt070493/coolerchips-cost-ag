def scale(scale_factor, param):
    """
    Rescales parameters by a specified factor

    Parameters
    ----------
    scale_factor: int or float
        Factor by which func will scale parameters
    param: list or array
        Parameters to be scaled
    Returns
    -------
    scaled_params: list or array
        Scaled parameter values
    """
    scaled_params = []
    for i in scale_factor:
        new_param = round(i * param)
        scaled_params.append(new_param)
    return scaled_params
