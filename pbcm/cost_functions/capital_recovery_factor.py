def calc_crf(discount, n) -> float:
    """
    Calculate capital recovery factor, CRF.

    Parameters
    __________
    discount: float
        discount rate selected to account for time value of money.
    n: int
        number of periods over which the capital is to be discounted.

    Returns
    -------
    crf: float
        capital recovery factor used in calculating the payment during a period.

    Notes
    _____
    Capital recovery factor is calculated as:
        ..math:: \frac{d(1+d)^n}{(1+d)^n-1}

    """
    crf = (discount * (1 + discount) ** n) / (
            (1 + discount) ** n - 1)

    return crf
