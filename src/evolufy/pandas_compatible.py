"""
Module for building a complete dataset from local directory with csv files.
"""
import logging
import os

import numpy as np
import pandas as pd
import regex as re
from zipline.data.bundles import core as bundles
from zipline.utils.cli import maybe_show_progress
import exchange_calendars as xcals


handler = logging.StreamHandler()
# handler = logging.StreamHandler(sys.stdout, format_string=" | {record.message}")
logger = logging.getLogger(__name__)
logger.handlers.append(handler)


def csvdir_equities(tframes=None, csvdir=None):
    """
    Generate an ingest function for custom data bundle
    This function can be used in ~/.zipline/extension.py
    to register bundle with custom parameters, e.g. with
    a custom trading calendar.

    Parameters
    ----------
    tframes: tuple, optional
        The data time frames, supported timeframes: 'daily' and 'minute'
    csvdir : string, optional, default: P_DIR environment variable
        The path to the directory of this structure:
        <directory>/<timeframe1>/<symbol1>.csv
        <directory>/<timeframe1>/<symbol2>.csv
        <directory>/<timeframe1>/<symbol3>.csv
        <directory>/<timeframe2>/<symbol1>.csv
        <directory>/<timeframe2>/<symbol2>.csv
        <directory>/<timeframe2>/<symbol3>.csv

    Returns
    -------
    ingest : callable
        The bundle ingest function

    Examples
    --------
    This code should be added to ~/.zipline/extension.py
    .. code-block:: python
       from zipline.data.bundles import csvdir_equities, register
       register('custom-csvdir-bundle',
                csvdir_equities(["daily", "minute"],
                '/full/path/to/the/csvdir/directory'))
    """

    return PandasCompatibleDIRBundle(tframes, csvdir).ingest


class PandasCompatibleDIRBundle:
    """
    Wrapper class to call csvdir_bundle with provided
    list of time frames and a path to the csvdir directory
    """

    def __init__(self, tframes=None, compatible_dir=None):
        self.tframes = tframes
        self.compatible_dir = compatible_dir

    def ingest(self, environ, asset_db_writer, minute_bar_writer, daily_bar_writer, adjustment_writer, calendar,
            start_session, end_session, cache, show_progress, output_dir, ):
        pandas_compatible_bundle(environ, asset_db_writer, minute_bar_writer, daily_bar_writer, adjustment_writer, calendar,
                                 start_session, end_session, cache, show_progress, output_dir, self.tframes, self.compatible_dir, )


@bundles.register("pandas_compatible_dir", calendar_name=os.environ.get('EXCHANGE_CALENDAR', 'NYSE'))
def pandas_compatible_bundle(environ, asset_db_writer, minute_bar_writer, daily_bar_writer, adjustment_writer, calendar: xcals.ExchangeCalendar,
                             start_session, end_session, cache, show_progress, output_dir, tframes=None, pandas_compatible_dir=None):
    """
    Build a zipline data bundle from the directory with csv files.
    """
    if not pandas_compatible_dir:
        pandas_compatible_dir = environ.get("P_DIR")
        if not pandas_compatible_dir:
            raise ValueError("P_DIR environment variable is not set")

    if not os.path.isdir(pandas_compatible_dir):
        raise ValueError("%s is not a directory" % pandas_compatible_dir)

    if not tframes:
        tframes = {"daily", "minute"}.intersection(os.listdir(pandas_compatible_dir))

        if not tframes:
            raise ValueError("'daily' and 'minute' directories " "not found in '%s'" % pandas_compatible_dir)

    divs_splits = {
        "divs": pd.DataFrame(columns=["sid", "amount", "ex_date", "record_date", "declared_date", "pay_date", ]),
        "splits": pd.DataFrame(columns=["sid", "ratio", "effective_date"]), }
    matcher = None
    for tframe in tframes:
        ddir = os.path.join(pandas_compatible_dir, tframe)

        symbols = sorted(matcher.group(1) for item in os.listdir(ddir) if os.path.isfile(os.path.join(ddir, item)) and (
            matcher := re.match('([^.,]+)', item, re.IGNORECASE)))
        if not symbols:
            raise ValueError("no <symbol> files found in %s" % ddir)

        dtype = [("start_date", "datetime64[ns]"), ("end_date", "datetime64[ns]"),
            ("auto_close_date", "datetime64[ns]"), ("symbol", "object"), ]
        metadata = pd.DataFrame(np.empty(len(symbols), dtype=dtype))

        if tframe == "minute":
            writer = minute_bar_writer
        else:
            writer = daily_bar_writer

        writer.write(_pricing_iter(ddir, symbols, metadata, divs_splits, show_progress, calendar=calendar), show_progress=show_progress)

        # Hardcode the exchange to "P_DIR" for all assets and (elsewhere)
        # register "P_DIR" to resolve to the NYSE calendar, because these
        # are all equities and thus can use the NYSE calendar.
        metadata["exchange"] = os.environ.get("EXCHANGE_CALENDAR", "NYSE")

        asset_db_writer.write(equities=metadata)

        divs_splits["divs"]["sid"] = divs_splits["divs"]["sid"].astype(int)
        divs_splits["splits"]["sid"] = divs_splits["splits"]["sid"].astype(int)
        adjustment_writer.write(splits=divs_splits["splits"], dividends=divs_splits["divs"])


def _pricing_iter(compatible_pandas_dir, symbols, metadata, divs_splits, show_progress, calendar: xcals.ExchangeCalendar):
    read_as = os.environ.get("READ_AS", "read_csv")
    with maybe_show_progress(symbols, show_progress, label="Loading custom pricing data: ") as it:
        # using scandir instead of listdir can be faster
        files = os.scandir(compatible_pandas_dir)
        # building a dictionary of filenames
        # NOTE: if there are duplicates it will arbitrarily pick the latest found
        fnames = {f.name.split(".")[0]: f.name for f in files if f.is_file()}

        for sid, symbol in enumerate(it):
            logger.debug(f"{symbol}: sid {sid}")
            fname = fnames.get(symbol, None)

            if fname is None:
                raise ValueError(f"{symbol} file is not in {compatible_pandas_dir}")

            if read_as == 'read_parquet':
                dfr = getattr(pd, read_as)(os.path.join(compatible_pandas_dir, fname)).sort_index()
            else:
                dfr = getattr(pd, read_as)(os.path.join(compatible_pandas_dir, fname), parse_dates=[0], index_col=0).sort_index()

            dfr = dfr[[calendar.is_session(dt) for dt in dfr.index]]
            start_date = dfr.index[0]
            end_date = dfr.index[-1]

            # The auto_close date is the day after the last trade.
            ac_date = end_date + pd.Timedelta(days=1)
            metadata.iloc[sid] = start_date, end_date, ac_date, symbol

            if "split" in dfr.columns:
                tmp = 1.0 / dfr[dfr["split"] != 1.0]["split"]
                split = pd.DataFrame(data=tmp.index.tolist(), columns=["effective_date"])
                split["ratio"] = tmp.tolist()
                split["sid"] = sid

                splits = divs_splits["splits"]
                index = pd.Index(range(splits.shape[0], splits.shape[0] + split.shape[0]))
                split.set_index(index, inplace=True)
                divs_splits["splits"] = pd.concat([splits, split], axis=0)

            if "dividend" in dfr.columns:
                # ex_date   amount  sid record_date declared_date pay_date
                tmp = dfr[dfr["dividend"] != 0.0]["dividend"]
                div = pd.DataFrame(data=tmp.index.tolist(), columns=["ex_date"])
                div["record_date"] = pd.NaT
                div["declared_date"] = pd.NaT
                div["pay_date"] = pd.NaT
                div["amount"] = tmp.tolist()
                div["sid"] = sid

                divs = divs_splits["divs"]
                ind = pd.Index(range(divs.shape[0], divs.shape[0] + div.shape[0]))
                div.set_index(ind, inplace=True)
                divs_splits["divs"] = pd.concat([divs, div], axis=0)

            yield sid, dfr


