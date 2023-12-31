from dataclasses import dataclass
import numpy as np
from typing import List, Optional
from darts import TimeSeries
from darts.dataprocessing.transformers import Scaler
from darts.models import (
    NBEATSModel,
)
import pyfolio as pf
import pandas as pd


def calculate_returns_from_prices(prices):
    prices = np.where(prices > 0, prices, 1e-9)
    returns = np.log10(prices[1:, :] / prices[:-1, :])
    return returns


@dataclass
class Inflation:
    inflation: List[float]


@dataclass
class AvailableInformation:
    assets: TimeSeries
    inflation: Optional[Inflation]
    risk_level: float = 1
    benchmark = '^MXX'

    def update_weight(self, index: int, entry: float):
        self.assets.static_covariates.iloc[index]['weight'] = entry

    def create_full_tear_sheet(self):
        df = self.assets.pd_dataframe()
        df.index = df.index.tz_localize('America/New_York')
        df['Portfolio'] = np.sum(df * np.array(self.assets.static_covariates['weight']), 1)
        returns = pd.DataFrame(calculate_returns_from_prices(df), columns=df.columns, index=df.index[1:])
        returns = returns[returns.index <= pd.Timestamp('2022-12-30', tz='America/New_York')]
        pf.create_full_tear_sheet(returns.Portfolio, live_start_date=pd.Timestamp('2022-01-01', tz='America/New_York'),
                                  benchmark_rets=returns[self.benchmark])
        pf.create_full_tear_sheet(returns[self.benchmark], live_start_date=pd.Timestamp('2022-01-01', tz='America/New_York'))
        return returns

    def valuate(self):
        pass


@dataclass
class NaiveMarketValuation(AvailableInformation):
    def valuate(self):
        return calculate_returns_from_prices(self.assets.values())


def softmax(x):
    return np.exp(x) / sum(np.exp(x))


@dataclass
class CapitalAssetPricingModel(AvailableInformation):
    def valuate(self):
        returns = np.array([
            calculate_returns_from_prices(asset.explore_returns().all_values().squeeze()) for asset in self.assets
        ])
        market = returns[:, -1]
        market_returns = np.dot(softmax(market), market)
        return


@dataclass
class MarketForecast(AvailableInformation):
    n: int = 365
    verbose: bool = True

    def valuate(self):
        market_price_forecasts = []
        assets = self.assets.split_after(pd.Timestamp('2022-01-01'))[0]
        for component in assets.components:
            if component == self.benchmark:
                continue
            scaler = Scaler()
            train = scaler.fit_transform(assets[component])
            model = NBEATSModel(input_chunk_length=24, output_chunk_length=30, n_epochs=20, activation='LeakyReLU',
                                num_layers=16)
            model.fit(train, verbose=self.verbose)
            market_price_forecasts.append(model.predict(n=self.n, verbose=self.verbose).values().squeeze())
        self.market_price_forecasts = np.array(market_price_forecasts).T
        return calculate_returns_from_prices(self.market_price_forecasts)


@dataclass
class DiscountedCashFlowValuation(AvailableInformation):
    def valuate(self):
        pass


@dataclass
class PiotroskiValuation(AvailableInformation):
    def valuate(self):
        pass
