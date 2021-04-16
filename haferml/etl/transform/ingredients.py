def convert_to_datetime(input_date, dayfirst=None, input_tz=None, output_tz=None):
    """
    Convert input to *datetime* object.
    This is the last effort of converting input to datetime.
    The order of instance check is
    1. datetime.datetime
    2. str
    3. float or int
    >>> handle_strange_dates(1531323212311)
    datetime(2018, 7, 11, 17, 33, 32, 311000)
    >>> handle_strange_dates(datetime(2085,1,1))
    datetime(2050, 1, 1)
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
