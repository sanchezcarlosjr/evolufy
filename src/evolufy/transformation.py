from typing import List

import numpy as np
import pandas as pd
from dagster import asset, ConfigurableResource
from darts import TimeSeries
from darts.utils import missing_values
from joblib import Parallel, delayed
from joblib_progress import joblib_progress
import exchange_calendars as xcals

from evolufy.data_sources import EvolufyPath
import subprocess


class DartsTimeSerieEvolufy(TimeSeries):
    def from_dataframe(symbol='', **kwargs):
        kwargs['freq'] = kwargs['freq'] if 'freq' in kwargs else 'B'
        kwargs['df'] = kwargs['df'].select_dtypes([np.number])
        return (missing_values.fill_missing_values(TimeSeries.from_dataframe(**kwargs), fill='auto',
                                                   method='akima').with_static_covariates(
            pd.DataFrame(data={"weight": [0], "shares": [0], "Symbol": [symbol]})))


class MarketMetrics(ConfigurableResource):
    metrics: List[str] = ['Close', 'Volume']
    market_calendar: str = "NYSE"


@asset(group_name="data_source_transformations", compute_kind="Transformations")
def darts_time_serie(market_metrics: MarketMetrics, filesystem: EvolufyPath, yahoo_finance_api: pd.DataFrame) -> List[str]:
    def save_file(symbol):
        (DartsTimeSerieEvolufy.from_dataframe(symbol=symbol,
                                              df=yahoo_finance_api[yahoo_finance_api['Symbol'] == symbol][
                                                  market_metrics.metrics]).to_pickle(
            filesystem.interim_path(f'darts/{symbol}.pkl')))
        return symbol

    symbols = yahoo_finance_api['Symbol'].unique()
    with joblib_progress("Transforming files...", total=len(symbols)):
        Parallel(n_jobs=4, backend='threading')(delayed(save_file)(symbol) for symbol in symbols)

    return [filesystem.interim_path(f'darts/{symbol}.pkl') for symbol in symbols]


@asset(group_name="data_source_transformations", compute_kind="Transformations")
def zipline_bundler(market_metrics: MarketMetrics, filesystem: EvolufyPath, yahoo_finance_api: pd.DataFrame):
    def save_file(symbol):
        (DartsTimeSerieEvolufy
         .from_dataframe(symbol=symbol, df=yahoo_finance_api[yahoo_finance_api['Symbol'] == symbol])
         .pd_dataframe()
         .rename(columns={
            'Close': 'close',
            'High': 'high',
            'Low': 'low',
            'Open': 'open',
            'Volume': 'volume'
        }).assign(dividend=0, split=0).to_parquet(filesystem.interim_path(f'zipline/daily/{symbol}.parquet')))
        return symbol

    symbols = yahoo_finance_api['Symbol'].unique()
    with joblib_progress("Transforming files...", total=len(symbols)):
        Parallel(n_jobs=4, backend='threading')(delayed(save_file)(symbol) for symbol in symbols)
    ZIPLINE_DIRECTORY = filesystem.interim_path('zipline')
    READ_AS = 'read_parquet'
    bundle = 'pandas_compatible_dir'
    subprocess.run(f'P_DIR={ZIPLINE_DIRECTORY} READ_AS={READ_AS} EXCHANGE_CALENDAR={market_metrics.market_calendar} zipline ingest -b {bundle}', shell=True)
