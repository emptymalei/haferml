import numpy as np
import pandas as pd
from loguru import logger


def count_column_values_within_ranges(df_inp, column_name, bins=None):
    """
    Count the number of values of a specific column according to the define ranges.

    :param pd.DataFrame df_inp: pandas dataframe
    :param column_name: column name to be counted
    :param bins: list of values to be used as the ranges
    """

    if bins is None:
        bins = np.arange(0, 7000, 100)

    all_values = df_inp[column_name].values

    # TODO: check type then convert
    all_values = all_values.astype(np.float)

    try:
        df_inp.loc[:, "count"] = pd.cut(df_inp[column_name].astype(float), bins)
    except Exception as e:
        print(e)
        print("pd.cut produces", pd.cut(df_inp[column_name].astype(float), bins))
        raise Exception("Can not set cut to column")

    df_counting = df_inp["count"].value_counts().sort_index()
    df_counting = df_counting.to_frame().reset_index()
    df_counting.columns = ["prices", "count"]
    df_counting.loc[:, "percent"] = df_counting["count"] / df_counting["count"].sum()
    couting_data = {
        "price": bins[:-1],
        "count": df_counting["count"].values,
        "percent": df_counting["percent"].values,
        "all_prices": all_values,
    }

    return couting_data


def count_column_values_within_ranges_two_levels_deep(
    df_inp,
    first_groupby_column_name,
    second_groupby_column_name,
    count_column_name,
    bins=None,
):
    """
    Count column values within ranges, but groupby twice in dataframe
    """

    if bins is None:
        logger.warning("No bins specified, will use a default range 0-10000")
        bins = np.arange(0, 10000, 100)

    df_first_groups = df_inp.groupby(first_groupby_column_name)
    list_of_first_groups = []
    return_data = {}

    for first_groups_key, one_df_of_first_groups in df_first_groups:
        list_of_first_groups.append(first_groups_key)
        counting_data_of_one_group = {}
        df_second_level_groups = one_df_of_first_groups.groupby(
            second_groupby_column_name
        )
        for second_groups_key, one_df_of_second_groups in df_second_level_groups:
            counting_data_of_one_group[
                second_groups_key
            ] = count_column_values_within_ranges(
                one_df_of_second_groups, count_column_name, bins
            )
        return_data[first_groups_key] = counting_data_of_one_group

    return return_data
