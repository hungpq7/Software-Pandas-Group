import copy 
import numpy as np
from skimage.util import view_as_windows

def get_X_y(series):
    """Return a windowed X, y from a timeseries `series`
    Args:
        series: pandas dataframe, shape n_days x m_stock
    Returns:
        X, y
    """
    # Data to train is the change percentage of the sotck values
    to_train = copy.deepcopy(series)
    to_train = to_train.diff(1)/to_train.shift(1)

    target_30d = copy.deepcopy(series)
    target_30d = -target_30d.diff(-30)/target_30d

    # Model params
    len_x = 120 #day(s)
    n_stock = 22 #stocks
    step  = 1   #day(s)

    X_full = view_as_windows(to_train.values, window_shape = (len_x, n_stock), step=step)
    X_full = np.squeeze(X_full)
    # Shape: (n_days , len_X, n_stocks)

    n_days = X_full.shape[0]

    # Remove the first 1 rows due to 1 day in diff(1) for the X <br>
    # and last 30 rows due to 29 day in diff(-30) for the y
    X = X_full[1:-30]
    y = target_30d.values[len_x:-30]

    # Remove nan values
    x_not_null = ~np.isnan(X).any(axis=1).any(axis=1)
    y_not_null = ~np.isnan(y).any(axis=1)

    not_null = x_not_null & y_not_null

    return X[not_null], y[not_null]