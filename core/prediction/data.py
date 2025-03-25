import pandas as pd

PATH = 'https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv'

def init_data():
    df = pd.read_csv(PATH)
    return df

def ingest_data():
    df = pd.read_csv(PATH)
    return df