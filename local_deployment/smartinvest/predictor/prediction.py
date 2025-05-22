import copy
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.losses import MeanSquaredError
from skimage.util import view_as_windows
import matplotlib.pyplot as plt
import io
import base64

class Predictor:
    def __init__(self, data_driver, model_path='smartinvest/model/exp_1.4_20250518.keras') -> None:
        self.model_path = model_path
        self.data_driver = data_driver

        self.model = tf.keras.models.load_model(self.model_path, custom_objects={'mse': MeanSquaredError()})
        print("MODEL SUMMARY: ", self.model.summary())

    @property
    def watch_list(self):
        wl = ['VCB', 'BID', 'FPT', 'HPG', 'GAS', 'CTG', 'VHM', 'TCB', 'VIC',
        'GVR', 'VPB', 'VNM', 'MBB', 'MSN', 'ACB', 'MWG', 'LPB',
        'HVN', 'BSR', 'SAB', 'HDB', 'BCM', 'VEA', 'PLX', 'STB', 'VJC',
        'VIB', 'SSB', 'SSI', 'FOX', 'DGC', 'VRE', 'SHB', 'TPB', 'POW',
        'BVH', 'REE', 'EIB', 'PNJ', 'KDH', 'OCB', 'MSB', 'GMD',
        'NVL', 'VND', 'FRT', 'VGC', 'KBC', 'VCI', 'DCM', 'HCM', 'PVS',
        'PDR', 'IDC', 'GEX', 'NAB', 'QNS', 'VHC', 'PVD',
        'NLG', 'KDC', 'DIG', 'HUT', 'MBS', 'HSG', 'VPI', 'DPM',
        'DHG', 'SHS', 'TCH', 'THD', 'PVI', 'HAG', 'VSH',
        'CMG', 'VCS', 'VCG', 'VIX', 'BAB', 'VTP', 'DGW',
        'PVT', 'HDG', 'DXG', 'PC1', 'BWE', 'SBT',
        'CEO', "DBC", "TCM"] 
        return wl

    def plot_predictions(self, predictions_df):
        """
        Create a bar chart visualization of the top 10 highest and lowest predictions.
        
        Args:
            predictions_df (pd.DataFrame): DataFrame containing 'stock' and 'prediction' columns
            
        Returns:
            str: Base64 encoded string of the plot image
        """
        plt.figure(figsize=(12, 6))
        
        # Sort predictions
        sorted_pred = predictions_df.sort_values('prediction', ascending=False)
        top_10 = sorted_pred.head(10)
        bottom_10 = sorted_pred.tail(10)
        
        # Combine top and bottom 10
        combined = pd.concat([top_10, bottom_10])
        
        # Create bar chart
        bars = plt.bar(combined['stock'], combined['prediction'])
        
        # Color bars based on prediction value
        for bar in bars:
            if bar.get_height() > 0:
                bar.set_color('green')
            else:
                bar.set_color('red')
        
        plt.title('Top 10 Buy-Sell Predictions')
        plt.xlabel('Stock Symbol')
        plt.ylabel('Prediction Value')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Convert plot to base64 string
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        plot_base64 = base64.b64encode(img.getvalue()).decode()
        plt.close()
        
        return plot_base64

    def get_prediction(self):
        interested_stocks = self.watch_list
        current_year = pd.Timestamp.now().year
        data = self.data_driver.read_stocks_years(interested_stocks, [current_year-1, current_year])
        
        X = self.preprocessing(data)
        print("DATA:", X.shape)
        y_pred = self.model.predict(X)
        print("Y_PRED: ", len(y_pred))

        result_df = pd.DataFrame({"stock":self.watch_list, "prediction": y_pred[-1]})
        result_df = result_df.sort_values(by="prediction", ascending=False)
        return result_df

    @staticmethod
    def clean_price(df_):
        df = df_.copy()
        prev_price = df.shift(1)
        
        # Chuyển sang delta-pct
        delta_pct = (df - prev_price)/prev_price
        

        # Giá trong 1 ngày không thể tăng quá biên độ 10% (HNX 10%, HSX 7%)
        # => Tất cả các thay đổi nhiều hơn khoảng này là do điều chỉnh giá => loại bỏ
        # Gán về thay đổi giá = 0
        delta_pct_adjusted = np.where( np.abs(delta_pct)<=0.1, delta_pct, 0 )

        i=0
        for col in df.columns:
            df[col] = delta_pct_adjusted[:,i]
            i+=1
        
        return (df+1).cumprod()

    @staticmethod
    def get_X(series, len_x=120, n_stock=22, step=1):
            """Return a windowed X, y from a timeseries `series`
            Args:
                series: pandas dataframe, shape n_days x m_stock

                # Model params
                len_x = 120 #day(s)
                n_stock = 22 #stocks
                step  = 1   #day(s)
            Returns:
                X, y
            """
            # Data to train is the change percentage of the sotck values
            to_train = copy.deepcopy(series)
            to_train = to_train.diff(1)/to_train.shift(1)

            # print("SHAPE: ", to_train.shape, len_x, n_stock)
            X_full = view_as_windows(to_train.values, window_shape = (len_x, n_stock), step=step)
            X_full = np.squeeze(X_full)
            # Shape: (n_days , len_X, n_stocks)

            n_days = X_full.shape[0]

            # Remove the first 1 rows due to 1 day in diff(1) for the X <br>
            # and last 30 rows due to 29 day in diff(-30) for the y
            X = X_full[1:]

            # Remove nan values
            x_not_null = ~np.isnan(X).any(axis=1).any(axis=1)

            return X[x_not_null]

    def preprocessing(self, data):
        # Bản chất của các ngày không giao dịch là giá giữ nguyên => sử dụng FFILL để fill NA
        data_full = data["Close"].ffill()

        data_full = self.clean_price(data_full)
        
        X = self.get_X(data_full, len_x=60, n_stock=data_full.shape[1])
        return X

