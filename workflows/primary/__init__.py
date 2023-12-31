from dagster import (Definitions, ScheduleDefinition, define_asset_job, load_assets_from_package_module,
                     AssetSelection, FilesystemIOManager)

from . import assets


defs = Definitions(
    assets=load_assets_from_package_module(assets),
    schedules=[
      ScheduleDefinition(job=define_asset_job(name="hacker_news_job", selection=AssetSelection.groups("hackernews")), cron_schedule="0 0 * * *")
    ],
    resources={
        'io_manager': FilesystemIOManager(base_dir="data/raw")
    }
)
