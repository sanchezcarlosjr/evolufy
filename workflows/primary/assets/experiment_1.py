import base64
import json
import os
from io import BytesIO

import matplotlib.pyplot as plt
import requests
from dagster import AssetExecutionContext, MaterializeResult, MetadataValue, asset
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine

msft = yf.Ticker("MSFT")

