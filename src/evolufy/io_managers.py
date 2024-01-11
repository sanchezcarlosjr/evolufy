import pandas as pd
import yfinance
from dagster import asset, ConfigurableResource, IOManager, io_manager, OutputContext, InputContext, EnvVar
from sqlalchemy import create_engine

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


@asset(group_name="market_information_providers", compute_kind="Evolufy Market Information Providers")
def yahoo_finance_tickets(yf: YahooFinanceResource) -> pd.DataFrame:
    """Get up to tickers

    API Docs: https://pypi.org/project/yfinance/
    """
    return (yf.download().stack().reset_index().set_index('Date').rename(index=str,
                                                                         columns={"level_1": "Symbol"}).sort_index())


class DataframeTableIOManager(IOManager):
    def __init__(self, db=None, schema=None):
        url = EnvVar('DATABASE_URL').get_value() if db is None else db
        self.schema = schema if schema else ""
        self.engine = create_engine(url)

    def handle_output(self, context: OutputContext, df: pd.DataFrame):
        table_name = self.get_table_name(context)
        df.to_sql(table_name, self.engine, if_exists='replace', schema=self.schema, index=True)

    def load_input(self, context: InputContext) -> pd.DataFrame:
        table_name = self.get_table_name(context)
        return pd.read_sql(f'SELECT * FROM {self.schema + table_name}', self.engine)

    def get_table_name(self, context):
        return context.asset_key.to_user_string() if context.name == 'result' else context.name


@io_manager
def df_table_io_manager():
    return DataframeTableIOManager()
