import pandas as pd
import pandas_datareader.data as web
from dagster import asset, ConfigurableResource
from zipline import run_algorithm
from zipline.api import symbol, order, record
from dagster import asset, file_relative_path, AssetIn, AssetExecutionContext, AutoMaterializePolicy

from evolufy.data_sources import EvolufyPath
from dagstermill import define_dagstermill_asset
import subprocess
import os
import nbformat
from nbconvert import MarkdownExporter, WebPDFExporter
from nbconvert.preprocessors import TagRemovePreprocessor
from traitlets.config import Config


class ExperimentSetting(ConfigurableResource):
    start: str = '2014'
    end: str = '2018'
    benchmark_returns: str = 'SP500'
    benchmark_returns_symbol: str = 'SPY'
    capital_base: int = 100000
    bundle: str = 'quandl'
    data_frequency: str = 'daily'
    live_start_date: str = '2017-01-01'
    round_trips: bool = True
    hide_positions: bool = True
    comment: str = ''


@asset(group_name="backtesting", io_manager_key='mem_io_manager', compute_kind="backtesting",
       deps=['darts_time_serie', 'zipline_bundler'])
def experiment_backtesting_1(context: AssetExecutionContext, experiment_setting: ExperimentSetting,
                             filesystem: EvolufyPath) -> dict:
    """
      Your algorithm
    """

    def initialize(context):
        context.asset = symbol('AAPL')
        context.shares = 100
        context.i = 0

    def handle_data(context, data):
        context.i = context.i % 365
        if context.i == 20:
            order(symbol('AAPL'), context.shares)
        if context.i == 364:
            order(symbol('AAPL'), -context.shares)
        context.i += 1

    start = pd.Timestamp(experiment_setting.start)
    end = pd.Timestamp(experiment_setting.end)

    sp500 = web.DataReader(experiment_setting.benchmark_returns, 'fred', start, end).SP500
    benchmark_returns = sp500.pct_change()

    perfomance = run_algorithm(start=start, end=end, initialize=initialize, handle_data=handle_data,
                               capital_base=experiment_setting.capital_base, benchmark_returns=benchmark_returns,
                               bundle=experiment_setting.bundle, data_frequency=experiment_setting.data_frequency)

    path = filesystem.processed_path(f'{context.run_id}/{context.asset_key.to_user_string()}.pkl')
    perfomance.to_pickle(path)
    perfomance.to_markdown(filesystem.processed_path(f'{context.run_id}/{context.asset_key.to_user_string()}.md'))

    return {
        'live_start_date': experiment_setting.live_start_date,
        'id': context.run_id,
        'experiment_path': path,
        'comment': experiment_setting.comment,
        'start': experiment_setting.start,
        'end': experiment_setting.end,
        'benchmark_returns_symbol': experiment_setting.benchmark_returns_symbol,
        'round_trips': experiment_setting.round_trips,
        'hide_positions': experiment_setting.hide_positions,
        'resultant_capital': perfomance.capital_used.sum()
    }


tear_sheet_jupyter_notebook = define_dagstermill_asset(name="full_tear_sheet",
                                                       notebook_path=file_relative_path(__file__,
                                                                                        "../../notebooks/1.0-cest-full-tear-sheet.ipynb"),
                                                       group_name="backtesting",
                                                       ins={"experiment_setting": AssetIn('experiment_backtesting_1')})


@asset(group_name="backtesting", auto_materialize_policy=AutoMaterializePolicy.eager(), io_manager_key='mem_io_manager',
       compute_kind="📝 reporting")
def report(context: AssetExecutionContext, filesystem: EvolufyPath, full_tear_sheet: bytes):
    notebook = nbformat.reads(full_tear_sheet.decode(), as_version=4)

    c = Config()
    c.MarkdownExporter.preprocessors = ['nbconvert.preprocessors.TagRemovePreprocessor']
    c.WebPDFExporter.preprocessors = ['nbconvert.preprocessors.TagRemovePreprocessor']
    c.TagRemovePreprocessor.enabled = True
    c.TagRemovePreprocessor.remove_cell_tags = ('remove_cell', 'injected-teardown', 'injected-parameters')
    c.MarkdownExporter.exclude_input = True
    c.WebPDFExporter.exclude_input = True

    md_exporter = MarkdownExporter(config=c)
    pdf_exporter = WebPDFExporter(config=c)
    md_exporter.register_preprocessor(TagRemovePreprocessor(config=c), enabled=True)
    pdf_exporter.register_preprocessor(TagRemovePreprocessor(config=c), enabled=True)

    body, _ = pdf_exporter.from_notebook_node(notebook)

    with open(filesystem.reports(f'experiment_{context.run_id}/report.pdf'), 'wb') as file:
        file.write(body)

    body, resources = md_exporter.from_notebook_node(notebook)

    with open(filesystem.reports(f'experiment_{context.run_id}/README.md'), 'w') as file:
        file.write(body)

    for key, resource in resources['outputs'].items():
        image_filename = filesystem.reports(f'experiment_{context.run_id}/{key}')
        with open(image_filename, 'wb') as file:
            file.write(resource)
