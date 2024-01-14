from darts.dataprocessing.transformers import Scaler
from darts.models import NBEATSModel
import pandas as pd
import numpy as np

def calculate_returns_from_prices(prices):
    prices = np.where(prices > 0, prices, 1e-9)
    returns = np.log10(prices[1:, :] / prices[:-1, :])
    return returns


def forecast_with_darts(self):
    market_price_forecasts = []
    assets = self.assets.split_after(pd.Timestamp('2022-01-01'))[0]
    for component in assets:
        scaler = Scaler()
        train = scaler.fit_transform(assets[component])
        model = NBEATSModel(input_chunk_length=24, output_chunk_length=30, n_epochs=20, activation='LeakyReLU',
                            num_layers=16)
        model.fit(train, verbose=self.verbose)
        market_price_forecasts.append(model.predict(n=self.n, verbose=self.verbose).values().squeeze())
    self.market_price_forecasts = np.array(market_price_forecasts).T
    return calculate_returns_from_prices(self.market_price_forecasts)
