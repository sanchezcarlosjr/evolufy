import pandas as pd
from workflows.primary.assets.experiment_1 import yahoo_finance_tickets


def test_load_yahoo_finance():
    df = yahoo_finance_tickets()
    assert df is not None
