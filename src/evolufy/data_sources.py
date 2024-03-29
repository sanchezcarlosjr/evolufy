import os
from pathlib import Path

import pandas as pd
import yfinance
from dagster import ConfigurableResource, asset

from evolufy.issuers import MexicanIssuers


class YahooFinanceResource(ConfigurableResource):
    # You need at least two tickers
    tickers: str = str(MexicanIssuers())
    start: str = '2013-01-01'
    end: str = None
    interval: str = '1d'
    period: str = 'max'

    def download(self) -> pd.DataFrame:
        return yfinance.download(tickers=self.tickers, start=self.start, end=self.end, period=self.period,
                                 interval=self.interval)


from functools import wraps


def recursive_mkdir(path):
    try:
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        pass
    return path


def ensure_valid_path(func):
    @wraps(func)
    def wrapper(*args, **kw):
        return recursive_mkdir(func(*args, **kw))

    return wrapper


def decorate_all_functions(function_decorator):
    def decorator(cls):
        for name, obj in vars(cls).items():
            if callable(obj) and name != "__init__":
                try:
                    obj = obj.__func__
                except AttributeError:
                    pass
                setattr(cls, name, function_decorator(obj))
        return cls

    return decorator


@decorate_all_functions(ensure_valid_path)
class EvolufyPath(ConfigurableResource):
    ROOT_DIR: str

    def cache(self, path=""):
        return os.path.join(self.ROOT_DIR, '.cache', path)

    def app_path(self, path=""):
        return os.path.join(self.ROOT_DIR, 'src/evolufy', path)

    def reports(self, path=""):
        return os.path.join(self.ROOT_DIR, 'reports', path)

    def __call__(self, path):
        return self.processed_path(path)

    def base_path(self, path=""):
        return os.path.join(self.ROOT_DIR, path)

    def data_path(self, path=""):
        return os.path.join(self.ROOT_DIR, 'data', path)

    def processed_path(self, path=""):
        return os.path.join(self.ROOT_DIR, 'data/processed', path)

    def external_path(self, path=""):
        return os.path.join(self.ROOT_DIR, 'data/external', path)

    def raw_path(self, path=""):
        return os.path.join(self.ROOT_DIR, 'data/raw', path)

    def interim_path(self, path=""):
        return os.path.join(self.ROOT_DIR, 'data/interim', path)


@asset(group_name="market_data_source", compute_kind="Market Data source")
def yahoo_finance_api(yf: YahooFinanceResource) -> pd.DataFrame:
    """
       API Docs: https://pypi.org/project/yfinance/
    """
    return (yf.download().stack().reset_index().set_index('Date').rename(index=str,
                                                                         columns={"level_1": "Symbol"}).sort_index())


@asset(group_name="market_data_source", compute_kind="Market Data source")
def data_bursatil_api_stocks() -> pd.DataFrame:
    """
       TODO
    """
    return pd.DataFrame({'x': ['']})
