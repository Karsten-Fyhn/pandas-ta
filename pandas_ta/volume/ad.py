# -*- coding: utf-8 -*-
from pandas_ta import Imports
from pandas_ta.utils import get_offset, non_zero_range, verify_series
from pandas import Series


def ad(high: Series, low: Series, close: Series, volume: Series, open_: Series = None, talib: bool = None,
       offset: int = None, **kwargs) -> Series:
    """Accumulation/Distribution (AD)

    Accumulation/Distribution indicator utilizes the relative position
    of the close to it's High-Low range with volume.  Then it is cumulated.

    Sources:
        https://www.tradingtechnologies.com/help/x-study/technical-indicator-definitions/accumulationdistribution-ad/

    Args:
        high (pd.Series): Series of 'high's
        low (pd.Series): Series of 'low's
        close (pd.Series): Series of 'close's
        volume (pd.Series): Series of 'volume's
        open_ (pd.Series): Series of 'open's
        talib (bool): If TA Lib is installed and talib is True, Returns the TA Lib
            version. Default: True
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)
        fill_method (value, optional): Type of fill method

    Returns:
        pd.Series: New feature generated.
    """
    # Validate Arguments
    high = verify_series(high)
    low = verify_series(low)
    close = verify_series(close)
    volume = verify_series(volume)
    offset = get_offset(offset)
    mode_tal = bool(talib) if isinstance(talib, bool) else True

    # Calculate Result
    if Imports["talib"] and mode_tal:
        from talib import AD
        ad = AD(high, low, close, volume)
    else:
        if open_ is not None:
            open_ = verify_series(open_)
            ad = non_zero_range(close, open_)  # AD with Open
        else:
            ad = 2 * close - (high + low)  # AD with High, Low, Close

        high_low_range = non_zero_range(high, low)
        ad *= volume / high_low_range
        ad = ad.cumsum()

    # Offset
    if offset != 0:
        ad = ad.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        ad.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        ad.fillna(method=kwargs["fill_method"], inplace=True)

    # Name and Categorize it
    ad.name = "AD" if open_ is None else "ADo"
    ad.category = "volume"

    return ad
