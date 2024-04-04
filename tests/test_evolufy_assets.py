import os

import numpy as np
import pandas as pd
from dagster import build_output_context, build_input_context
from sqlalchemy import create_engine

from evolufy.data_sources import yahoo_finance_api, YahooFinanceResource, EvolufyPath
from evolufy.io_managers import DataframeTableIOManager
from evolufy.transformation import DartsTimeSerieEvolufy, darts_time_serie, MarketMetrics
import random
from dotenv import load_dotenv

from evolufy.valuation import valuate_with_capital_asset_pricing_model

load_dotenv()


def test_yahoo_finance_extraction():
    df: pd.DataFrame = yahoo_finance_api(YahooFinanceResource(tickers='AAPL SPY'))
    assert df is not None
    assert (['Symbol', 'Adj Close', 'Close', 'High', 'Low', 'Open', 'Volume'] == df.columns).all()
    assert (['AAPL', 'SPY'] == df['Symbol'].unique()).all()


def test_df_table_io_manager_handle_output():
    os.environ['DATABASE_URL'] = 'sqlite+pysqlite:///:memory:'
    io_mgr = DataframeTableIOManager()
    context = build_output_context(name="evolufy_history", step_key="123")
    io_mgr.handle_output(context, pd.DataFrame({'Symbol': ['A', 'B']}))

    df = pd.read_sql('SELECT * FROM evolufy_history', io_mgr.engine)
    assert 'Symbol' in df.columns
    assert df['Symbol'].isin(['A', 'B']).all()


def test_df_table_io_manager_handle_input():
    os.environ['DATABASE_URL'] = 'sqlite+pysqlite:///:memory:'

    task = "evolufy_history"
    io_mgr = DataframeTableIOManager(index_col=None, parse_dates=[])
    df = pd.DataFrame({'Symbol': ['A', 'B']})
    io_mgr.handle_output(build_output_context(name=task, step_key="123"), df)

    df2 = io_mgr.load_input(build_input_context(upstream_output=build_output_context(name=task, step_key="123")))

    assert (df2['Symbol'] == df['Symbol']).all()


def test_dataframe_extraction_into_darts():
    dates = pd.date_range('1/1/2000', periods=8, freq='B')

    df = pd.DataFrame(np.random.randn(8, 4), index=dates, columns=['A', 'B', 'C', 'D'])

    timeseries = DartsTimeSerieEvolufy.from_dataframe(df=df)
    assert timeseries.static_covariates.shape == (1, 3)
    assert (timeseries.columns == df.columns).all()
    assert (timeseries.pd_dataframe().equals(df))


def test_stock_dataset_into_darts_object_transformation():
    n = 10
    dates = pd.date_range('1/1/2000', periods=n, freq='B')
    df = pd.DataFrame(np.random.randn(n, 4), index=dates, columns=['Symbol', 'Close', 'C', 'D'])
    symbol = [random.choice(['A', 'B']) for i in range(n)]
    df = df.assign(Symbol=symbol)
    filesystem = EvolufyPath(ROOT_DIR=os.environ['ROOT_DIR'])
    symbols = darts_time_serie(MarketMetrics(metrics=['Close']), filesystem=filesystem, yahoo_finance_api=df)
    timeserie = DartsTimeSerieEvolufy.from_pickle(filesystem.interim_path(f'darts/{symbol}.pkl')).pd_dataframe()
    assert (timeserie.columns == ['Close'])
    asset = df[df['Symbol'] == symbol]['Close']
    assert (timeserie['Close'] == asset).all()
    assert symbols[0] == filesystem.interim_path(f'darts/{symbol}.pkl')


def test_training():
    n = 10
    dates = pd.date_range('1/1/2000', periods=n, freq='B')
    df = pd.DataFrame(np.random.randn(n, 4), index=dates, columns=['Symbol', 'Close', 'C', 'D'])
    symbol = 'A'
    df = df.assign(Symbol=symbol)
    filesystem = EvolufyPath(ROOT_DIR=os.environ['ROOT_DIR'])
    symbols = darts_time_serie(MarketMetrics(metrics=['Close']), filesystem=filesystem, yahoo_finance_api=df)
    x = valuate_with_capital_asset_pricing_model(symbols)
    assert False
