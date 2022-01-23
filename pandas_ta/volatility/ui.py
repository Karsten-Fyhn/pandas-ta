# -*- coding: utf-8 -*-
from numpy import sqrt as npsqrt
from pandas_ta.overlap import sma
from pandas import Series
from pandas_ta.utils import get_offset, verify_series


def ui(close: Series, length: int = None, scalar: int = None, offset: int = None, **kwargs) -> Series:
    """Ulcer Index (UI)

    The Ulcer Index by Peter Martin measures the downside volatility with the use of
    the Quadratic Mean, which has the effect of emphasising large drawdowns.

    Sources:
        https://library.tradingtechnologies.com/trade/chrt-ti-ulcer-index.html
        https://en.wikipedia.org/wiki/Ulcer_index
        http://www.tangotools.com/ui/ui.htm

    Args:
        high (pd.Series): Series of 'high's
        close (pd.Series): Series of 'close's
        length (int): The short period.  Default: 14
        scalar (float): A positive float to scale the bands. Default: 100
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)
        fill_method (value, optional): Type of fill method
        everget (value, optional): TradingView's Evergets SMA instead of SUM
            calculation. Default: False

    Returns:
        pd.Series: New feature
    """
    # Validate arguments
    length = int(length) if length and length > 0 else 14
    scalar = float(scalar) if scalar and scalar > 0 else 100
    close = verify_series(close, length)
    offset = get_offset(offset)

    if close is None: return

    # Calculate Result
    highest_close = close.rolling(length).max()
    downside = scalar * (close - highest_close)
    downside /= highest_close
    d2 = downside * downside

    everget = kwargs.pop("everget", False)
    if everget:
        # Everget uses SMA instead of SUM for calculation
        ui = (sma(d2, length) / length).apply(npsqrt)
    else:
        ui = (d2.rolling(length).sum() / length).apply(npsqrt)

    # Offset
    if offset != 0:
        ui = ui.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        ui.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        ui.fillna(method=kwargs["fill_method"], inplace=True)

    # Name and Categorize it
    ui.name = f"UI{'' if not everget else 'e'}_{length}"
    ui.category = "volatility"

    return ui
