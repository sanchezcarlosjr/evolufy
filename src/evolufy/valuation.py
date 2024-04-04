from typing import List

import pandas as pd
from dagster import asset

from evolufy.data_sources import EvolufyPath
from evolufy.transformation import darts_time_serie
import darts

@asset(group_name="valuation", compute_kind="Asset Valuation")
def valuate_with_capital_asset_pricing_model(darts_time_serie: List[str]) -> pd.DataFrame:
    ts = darts.TimeSeries.from_pickle(darts_time_serie[0])
    RF = 0
    M = []
    R = ts['Close'][:100]
    beta = 0
    Ef = RF + beta*(M-RF)
    return pd.DataFrame([])
