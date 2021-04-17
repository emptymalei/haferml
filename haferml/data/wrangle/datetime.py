import datetime
from loguru import logger

import dateutil
import pandas as pd


def convert_to_datetime(input_date, dayfirst=None, input_tz=None, output_tz=None):
    """
    Convert input to *datetime* object.
    This is the last effort of converting input to datetime.
    The order of instance check is
    1. datetime.datetime
    2. str
    3. float or int

    ```
    >>> handle_strange_dates(1531323212311)
    datetime(2018, 7, 11, 17, 33, 32, 311000)
    >>> handle_strange_dates(datetime(2085,1,1))
    datetime(2050, 1, 1)
    ```

    :param input_date: input data of any possible format
    :param input_tz: input timezone, defaults to utc
    :param output_tz: output timezone, defaults to utc
    :return: converted datetime format
    :rtype: datetime.datetime
    """
    if dayfirst is None:
        dayfirst = True
    if input_tz is None:
        input_tz = datetime.timezone.utc
    if output_tz is None:
        output_tz = datetime.timezone.utc

    res = None
    if isinstance(input_date, datetime.datetime):
        res = input_date
        if input_tz:
            res = res.replace(tzinfo=input_tz)
        if output_tz:
            res = res.astimezone(output_tz)
    elif isinstance(input_date, str):
        try:
            res = dateutil.parser.parse(input_date, dayfirst=dayfirst)
            if input_tz:
                res = res.replace(tzinfo=input_tz)
            if output_tz:
                res = res.astimezone(output_tz)
        except:
            logger.warning(f"Could not convert {input_date} to datetime!")
            pass
    elif isinstance(input_date, (float, int)):
        try:
            res = datetime.datetime.utcfromtimestamp(input_date / 1000)
            if input_tz:
                res = res.replace(tzinfo=input_tz)
            if output_tz:
                res = res.astimezone(output_tz)
        except:
            logger.warning(f"Could not convert {input_date} to datetime!")
            pass
    else:
        raise Exception(
            "Could not convert {} to datetime: type {} is not handled".format(
                input_date, type(input_date)
            )
        )

    return res


def unpack_datetime(data):
    """
    unpack_datetime converts datetime (string) to a dict of useful date information
    """
    res = {}
    dt = convert_to_datetime(data, dayfirst=False)
    if dt:
        try:
            res["year"] = dt.year
        except Exception as e:
            logger.error(f"Could not find year for {dt} (raw: {data})")

        try:
            res["month"] = dt.month
        except Exception as e:
            logger.error(f"Could not find month for {dt} (raw: {data})")

        try:
            res["day"] = dt.day
        except Exception as e:
            logger.error(f"Could not find day for {dt} (raw: {data})")

        try:
            res["weekday"] = dt.weekday() + 1
        except Exception as e:
            logger.error(f"Could not find weekday for {dt} (raw: {data})")

    return res


def date_range_has_weekday(dt_start, dt_end):
    """
    date_range_has_weekday decides if the given date range contains weekday

    :param dt_start: datetime of the start of date range
    :param dt_end: datetime of the end of date range
    """
    res = []

    if pd.isnull(dt_start) or pd.isnull(dt_end):
        logger.warning(f"date start end not specified: {dt_start}, {dt_end}")
        return None

    if isinstance(dt_start, str):
        dt_start = pd.to_datetime(dt_start)
    if isinstance(dt_end, str):
        dt_end = pd.to_datetime(dt_end)

    for dt in pd.date_range(dt_start, dt_end):
        if dt.weekday() < 5:
            res.append(True)
        else:
            res.append(False)

    return True in res
