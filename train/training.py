import os
import glob

import scipy
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from skimage.util import view_as_windows
from sklearn.metrics import mean_absolute_error
import tensorflow as tf

from smartinvest.datadriver.data_processing import read_stocks_years

import vnstock

l_stock = ['ACB', 'BAB', 'BBS', 'BCM', 'BID', 'BSR', 'BVH', 'BWE', 'CCT',
       'CEO', 'CMG', 'CTG', 'DBC', 'DCM', 'DGC', 'DGW', 'DHG', 'DIG',
       'DPM', 'DTK', 'DXG', 'EIB', 'EVF', 'FOX', 'FPT', 'FRT', 'FTS',
       'GAS', 'GEX', 'GMD', 'GVR', 'HAG', 'HCM', 'HDB', 'HDG', 'HPG',
       'HSG', 'HUT', 'HVN', 'IDC', 'IDP', 'KBC', 'KDC', 'KDH', 'KSF',
       'LGC', 'LPB', 'MBB', 'MBS', 'MCH', 'MSB', 'MSN', 'MWG', 'NAB',
       'NLG', 'NVL', 'OCB', 'PC1', 'PDR', 'PGV', 'PHP', 'PLX', 'PNJ',
       'POW', 'PVD', 'PVI', 'PVS', 'PVT', 'QNS', 'REE', 'SAB', 'SBT',
       'SHB', 'SHS', 'SSB', 'SSI', 'STB', 'TCB', 'TCH', 'TCM', 'THD',
       'TPB', 'VCB', 'VCG', 'VCI', 'VCS', 'VEA', 'VGC', 'VHC', 'VHM',
       'VIB', 'VIC', 'VIX', 'VJC', 'VND', 'VNM', 'VPB', 'VPI', 'VRE',
       'VSH', 'VTP']

data = read_stocks_years(l_stock, year_from=2019, year_to=2022)

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


train_split = '2020-12-31'
test_split = '2022-01-01'
data_train = data[["Close"]][data.index <= train_split]
data_valid = data[["Close"]][ (data.index > train_split)&((data.index < test_split))]
data_test = data[["Close"]][data.index >= test_split]

X_train, y_train = get_X_y( data_train )
X_valid, y_valid = get_X_y( data_valid )
X_test, y_test   = get_X_y( data_test )

input_with = 120
num_label = y_train.shape[-1]

model = tf.keras.models.Sequential([
    tf.keras.layers.Bidirectional(
        tf.keras.layers.LSTM( input_with, return_sequences=0)),
    # tf.keras.layers.BatchNormalization(),
    # tf.keras.layers.Dense( out_steps*num_label*4, activation='relu' ),
    # tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense( num_label, activation=None ),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense( num_label)
])

MAX_EPOCHS = 60
patience=5
early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss',
                                                patience=patience,
                                                mode='min')

model.compile(loss='mse',
            optimizer=tf.optimizers.Adam(clipvalue=0.1, learning_rate=0.001),
            metrics=[tf.metrics.MeanAbsoluteError()])

history = model.fit(X_train,y_train, epochs=MAX_EPOCHS, batch_size=128,
                    validation_data = (X_valid, y_valid),
                    callbacks=[early_stopping], verbose= 1)

y_test_pred = model.predict(X_test)