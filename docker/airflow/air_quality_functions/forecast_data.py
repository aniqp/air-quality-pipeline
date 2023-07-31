import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
from prophet import Prophet
from prophet import Prophet
import datetime
import json
from air_quality_functions.process_data import map_hour_to_column

def train_model(data):
    df = pd.DataFrame(data)
    df = df.rename(columns={df.columns[0]: 'date'})
    column_mappings = {old_col: old_col -1 for old_col in df.columns[1:]}
    df = df.rename(columns = column_mappings)
    df_melt = pd.melt(df, id_vars = 'date', var_name = 'Hour')
    df_melt['Hour'] = df_melt['Hour'].apply(lambda x: datetime.time(hour = x, minute = 0, second = 0))
    df_melt['datetime'] = df_melt.apply(lambda x: datetime.datetime.combine(x['date'], x['Hour']), axis = 1)

    analysis = df_melt[['datetime', 'value']]
    analysis = analysis.rename(columns = {'datetime': 'ds', 'value': 'y'})
    analysis = analysis[analysis['ds'] >= pd.to_datetime('2023-05-29')]

    m = Prophet(changepoint_prior_scale=1, seasonality_prior_scale = 10)
    m.fit(analysis)
    future = m.make_future_dataframe(periods=24, freq = 'H')
    forecast = m.predict(future)
    predictions = forecast[['ds', 'yhat']].tail(24)

    date = predictions['ds'].iloc[0].date()
    values = list(predictions['yhat'].values)

    return date, values