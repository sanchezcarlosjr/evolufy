import os

from dagster import (Definitions, ScheduleDefinition, define_asset_job, load_assets_from_package_module,
                     AssetSelection, EnvVar)

from evolufy.backtesting import ExperimentSetting
from evolufy.data_sources import YahooFinanceResource, Filesystem
# from . import assets
from evolufy.io_managers import DataframeTableIOManager
import evolufy
from evolufy.transformation import MarketMetrics
from dagster_mlflow import mlflow_tracking
from dagstermill import ConfigurableLocalOutputNotebookIOManager
from dagster import fs_io_manager

mlflow = mlflow_tracking.configured({
    "experiment_name": "backtesitng",
    "mlflow_tracking_uri": os.environ['MLFLOW_TRACKING_URI'],
    "extra_tags": {"super": "experiment"}
})

defs = Definitions(
    assets=load_assets_from_package_module(evolufy),
    schedules=[
        ScheduleDefinition(job=define_asset_job(
            name="extraction_job",
            selection=AssetSelection.groups("market_information_providers")),
            cron_schedule="0 0 * * *",
            execution_timezone='America/Tijuana'
        )
    ],
    resources={
        'io_manager': DataframeTableIOManager(schema="evolufy"),
        'yf': YahooFinanceResource(),
        'market_metrics': MarketMetrics(),
        'filesystem': Filesystem(ROOT_DIR=EnvVar("ROOT_DIR")),
        'experiment_setting': ExperimentSetting(),
        "output_notebook_io_manager": ConfigurableLocalOutputNotebookIOManager(base_dir='./data/reports'),
        'mem_io_manager':  fs_io_manager
    }
)
