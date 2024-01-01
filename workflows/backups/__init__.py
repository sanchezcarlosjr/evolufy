from dagster import (Definitions, ScheduleDefinition, define_asset_job, load_assets_from_package_module,
                     AssetSelection, FilesystemIOManager, OpExecutionContext)
from dagster import op, job, Config
import os
from dagster import sensor, RunRequest, RunConfig


class FileConfig(Config):
    filename: str


@op
def process_file(context: OpExecutionContext, config: FileConfig):
    context.log.info(config.filename)


@job
def log_file_job():
    process_file()


@sensor(job=log_file_job)
def data_directory_sensor():
    for root, dirs, files in os.walk('./data'):
        for name in files:
            filename = os.path.join(root, name)
            yield RunRequest(
                run_key=filename,
                run_config=RunConfig(
                    ops={"process_file": FileConfig(filename=filename)}
                ),
            )


defs = Definitions(
    jobs=[log_file_job],
    sensors=[data_directory_sensor]
)
