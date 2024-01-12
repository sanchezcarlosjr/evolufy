from typing import List

import numpy as np
import pandas as pd
from dagster import asset, ConfigurableResource
from darts import TimeSeries
from darts.utils import missing_values
from joblib_progress import joblib_progress

from evolufy.data_sources import Filesystem
from joblib import Memory, Parallel, delayed


class DartsTimeSerieEvolufy(TimeSeries):
    def from_dataframe(symbol='',**kwargs):
        kwargs['freq'] = kwargs['freq'] if 'freq' in kwargs else 'B'
        kwargs['df'] = kwargs['df'].select_dtypes([np.number])
        return (missing_values.fill_missing_values(TimeSeries.from_dataframe(**kwargs), fill='auto',
                                                   method='pchip').with_static_covariates(pd.DataFrame(
            data={"weight": [0], "shares": [0], "Symbol": [symbol]})))


class MarketMetrics(ConfigurableResource):
    metrics: List[str] = ['Adj Close', 'Volume']


@asset(group_name="data_source_transformartions", compute_kind="Transformations")
def darts_time_serie(market_metrics: MarketMetrics, filesystem: Filesystem, yahoo_finance_api: pd.DataFrame):
    def save_file(symbol):
        (DartsTimeSerieEvolufy.from_dataframe(
            symbol=symbol,
            df=yahoo_finance_api[yahoo_finance_api['Symbol'] == symbol][market_metrics.metrics]).to_pickle(
            filesystem.interim_path(f'{symbol}.pkl')))
        return symbol

    symbols = yahoo_finance_api['Symbol'].unique()
    with joblib_progress("Transforming files...", total=len(symbols)):
        Parallel(n_jobs=4, backend='threading')(delayed(save_file)(symbol) for symbol in symbols)
