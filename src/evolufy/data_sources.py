import glob
import os
import json
from typing import Tuple

import pandas as pd
import darts
from evolufy.information import *
from dataclasses import dataclass
import asyncio
from dacite import from_dict
import yfinance as yf
import pathlib


def read_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return {}


class DataService:
    async def request(self):
        try:
            return await self.fetch()
        except:
            return {}


@dataclass(init=False)
class DataServices:
    information: type  # type of AvailableInformation
    data_services: Tuple[DataService]

    def __init__(self, information: type, *args: DataService):
        self.data_services = args
        self.information = information

    async def request(self):
        results = await asyncio.gather(*[ds.request() for ds in self.data_services])
        acc = {}
        for result in results:
            acc.update(result)
        return from_dict(data_class=self.information, data=acc)


# https://site.financialmodelingprep.com/login
class FinancialAPI(DataService):
    async def fetch(self):
        return {'inflation': {'inflation': []}}


class Filesystem(DataService):
    def __init__(self, *paths):
        if not paths:
            paths = ["**/*.json"]
        self.paths = paths

    async def fetch(self):
        files = []
        for path in self.paths:
            files.extend(glob.glob(path))
        assets = []
        for file in files:
            df = pd.read_json(file).drop(columns=['import']).set_index('date').rename(columns={'price': pathlib.Path(file).stem})
            if len(df) >= 100:
                assets.append(df)
        timeserie = darts.utils.missing_values.fill_missing_values(TimeSeries.from_dataframe(pd.concat(assets).interpolate(), freq='B'), fill='auto', method='pchip')
        timeserie.with_static_covariates(pd.DataFrame(data={"weight": np.zeros(timeserie.n_components)}))
        return timeserie


class YahooFinance(DataService):
    def __init__(self, *assets):
        self.assets = assets
        self.benchmark = '^MXX'

    async def fetch(self):
        adj_closes = yf.download([*self.assets, self.benchmark])['Adj Close']
        adj_closes = adj_closes.dropna()
        if len(adj_closes) == 1:
            adj_closes = pd.DataFrame({self.assets[0]: adj_closes})
        timeserie = darts.utils.missing_values.fill_missing_values(TimeSeries.from_dataframe(adj_closes, freq='B'), fill='auto', method='pchip')
        timeserie = timeserie.with_static_covariates(pd.DataFrame(data={
            "weight": np.zeros(timeserie.n_components),
            "shares": np.zeros(timeserie.n_components)
        }))
        return {'assets': timeserie, 'benchmark': self.benchmark}


# https://databursatil.com/
async def fetch():
    return {'inflation': {'inflation': []}}


class DataBursatil(DataService):
    pass
