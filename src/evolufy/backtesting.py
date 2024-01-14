import pandas as pd
import pandas_datareader.data as web
from dagster import asset, ConfigurableResource
from zipline import run_algorithm
from zipline.api import symbol, order, record
from dagster import asset, file_relative_path, AssetIn, AssetExecutionContext

from evolufy.data_sources import Filesystem
from dagstermill import define_dagstermill_asset
import subprocess
import os
class ExperimentSetting(ConfigurableResource):
    start: str = '2014'
    end: str = '2018'
    benchmark_returns: str = 'SP500'
    capital_base: int = 100000
    bundle: str = 'quandl'
    data_frequency: str = 'daily'


@asset(group_name="backtesting", io_manager_key='mem_io_manager', compute_kind="backtesting",
       deps=['darts_time_serie', 'zipline_bundler'])
def experiment_backtesting_1(experiment_setting: ExperimentSetting, filesystem: Filesystem) -> str:
    """
      Your algorithm
    """

    def initialize(context):
        context.asset = symbol('AAPL')

    def handle_data(context, data):
        order(symbol('AAPL'), 10)
        record(AAPL=data.current(symbol('AAPL'), "price"))

    start = pd.Timestamp(experiment_setting.start)
    end = pd.Timestamp(experiment_setting.end)

    sp500 = web.DataReader(experiment_setting.benchmark_returns, 'fred', start, end).SP500
    benchmark_returns = sp500.pct_change()

    results = run_algorithm(start=start, end=end, initialize=initialize,
                            handle_data=handle_data, capital_base=experiment_setting.capital_base,
                            benchmark_returns=benchmark_returns,
                            bundle=experiment_setting.bundle, data_frequency=experiment_setting.data_frequency)

    results.to_html(filesystem.processed_path('experiment_1.html'))
    results.to_pickle(filesystem.processed_path('experiment_1.pkl'))

    return '2016-01-01'


tear_sheet_jupyter_notebook = define_dagstermill_asset(
    name="full_tear_sheet",
    notebook_path=file_relative_path(__file__, "../../notebooks/1.0-cest-full-tear-sheet.ipynb"),
    group_name="backtesting",
    ins={"live_start_date": AssetIn('experiment_backtesting_1')}
)


@asset(group_name="backtesting", io_manager_key='mem_io_manager', compute_kind="backtesting")
def report(context: AssetExecutionContext, filesystem: Filesystem, full_tear_sheet: str):
    NOTEBOOK = filesystem.reports('full_tear_sheet.ipynb')
    OUTPUT = filesystem.reports(f'experiment_{context.run_id}/full_tear_sheet.md')
    subprocess.run(f'jupyter nbconvert {NOTEBOOK} --TagRemovePreprocessor.enabled=True --TagRemovePreprocessor.remove_cell_tags remove_cell --TemplateExporter.exclude_input=True  --to markdown --output {OUTPUT}', shell=True)
    os.remove(NOTEBOOK)
    subprocess.run(f'git add . && dvc add data/data data/external data/external data/interim data/processed data/raw '
                   f'&& git commit -m "new experiment with id {context.run_id}"')
