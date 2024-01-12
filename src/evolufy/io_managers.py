import pandas as pd
from dagster import IOManager, io_manager, OutputContext, InputContext, EnvVar
from sqlalchemy import create_engine


class DataframeTableIOManager(IOManager):
    def __init__(self, db=None, schema=None, index_col='Date', parse_dates=None):
        if parse_dates is None:
            parse_dates = ['Date']
        url = EnvVar('DATABASE_URL').get_value() if db is None else db
        self.schema = schema if schema else ""
        self.engine = create_engine(url)
        self.index_col = index_col
        self.parse_dates = parse_dates

    def handle_output(self, context: OutputContext, df: pd.DataFrame):
        if df is None or not isinstance(df, pd.DataFrame):
            return
        table_name = self.get_table_name(context)
        df.to_sql(table_name, self.engine, if_exists='replace', schema=self.schema, index=True)

    def load_input(self, context: InputContext) -> pd.DataFrame:
        table_name = (self.schema + '.' if self.schema else "") + self.get_table_name(context.upstream_output)
        return pd.read_sql(f'SELECT * FROM {table_name}', self.engine, index_col=self.index_col, parse_dates=self.parse_dates)

    def get_table_name(self, context):
        return context.asset_key.to_user_string() if context.name == 'result' else context.name


@io_manager
def df_table_io_manager():
    return DataframeTableIOManager()
