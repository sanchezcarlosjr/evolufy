import os
import sys
import math
import logging
from pathlib import Path

import numpy as np
import scipy as sp
import sklearn
# import statsmodels.api as sm
# from statsmodels.formula.api import ols
import pystow

import matplotlib as mpl
import matplotlib.pyplot as plt
import yfinance as yf
import regex as re
import seaborn as sns

sns.set_context("poster")
sns.set(rc={"figure.figsize": (16, 9.)})
sns.set_style("whitegrid")

import pandas as pd
pd.set_option("display.max_rows", 120)
pd.set_option("display.max_columns", 120)

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

ROOT_DIR = re.sub(r"\/$", "", os.environ['ROOT_DIR'])


def app_path(path=""):
    return os.path.join(ROOT_DIR, 'src/evolufy', path)


def base_path(path=""):
    return os.path.join(ROOT_DIR, path)


def data_path(path=""):
    return os.path.join(ROOT_DIR, 'data', path)


def reports(path=""):
    path = os.path.join(ROOT_DIR, 'data/reports', path)
    try:
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        pass
    return os.path.join(ROOT_DIR, 'data/reports', path)


def processed_path(path=""):
    return os.path.join(ROOT_DIR, 'data/processed', path)


def external_path(path=""):
    return os.path.join(ROOT_DIR, 'data/external', path)


def raw_path(path=""):
    return os.path.join(ROOT_DIR, 'data/raw', path)


def interim_path(path=""):
    return os.path.join(ROOT_DIR, 'data/interim', path)
