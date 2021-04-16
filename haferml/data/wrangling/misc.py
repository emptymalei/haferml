from ast import literal_eval

from loguru import logger


def get_value_in_dict_recursively(dictionary, path, ignore_path_fail=None):
    """
    Get value of a dictionary according to specified path (names)

    :param dict dictionary: input dictionary
    :param list path: path to the value to be obtained

    This function always returns the value or None.

    >>> get_value_in_dict_recursively({'lvl_1':{'lvl_2':{'lvl_3':'lvl_3_value'}}},['lvl_1','lvl_3'])
    {'lvl_3':'lvl_3_value'}
    >>> get_value_in_dict_recursively({1:{2:{3:'hi'}}},[1,'2',3])
    {'hi'}
    """
    if ignore_path_fail is None:
        ignore_path_fail = True

    if isinstance(path, list):
        path_temp = path.copy()
    elif isinstance(path, tuple):
        path_temp = list(path).copy()
    else:
        logger.warning(f"path is not list or tuple, converting to list: {path}")
        path_temp = [path].copy()

    if len(path_temp) > 1:
        pop = path_temp.pop(0)
        try:
            pop = int(pop)
        except ValueError:
            if ignore_path_fail:
                logger.warning(f"can not get path")
                pass
            else:
                raise Exception(f"specified path ({path}) is not acceptable")

        try:
            return get_value_in_dict_recursively(dictionary[pop], path_temp)
        except:
            logger.debug(f"did not get values for {pop}")
            return None
    elif len(path_temp) == 0:
        return None
    else:
        try:
            val = int(path_temp[0])
        except:
            val = path_temp[0]
        try:
            return dictionary[val]
        except KeyError:
            logger.error(f"KeyError: Could not find {path_temp[0]}")
            return None
        except TypeError:
            logger.error(f"TypeError: Could not find {path_temp[0]}")
            return None


###############
# Generic
###############


def convert_str_repr_to_list(inp):
    """
    convert_str_repr_to_list concerts string representation of list to list
    """

    res = []
    if isinstance(inp, str):
        try:
            res = literal_eval(inp)
        except Exception as e:
            raise Exception(f"Could not convert {inp} to list")
    elif isinstance(inp, (list, tuple, set)):
        res = list(inp)

    return res


def convert_str_repr_to_tuple(inp):
    """
    convert_str_repr_to_tuple converts string representation of tuple to tuple
    """

    res = []
    if isinstance(inp, str):
        try:
            res = literal_eval(inp)
        except Exception as e:
            raise Exception(f"Could not convert {inp} to list")
    if isinstance(inp, (list, tuple, set)):
        res = tuple(inp)

    return res


def convert_to_bool(data):
    """
    convert_to_bool converts input to bool type in python.

    The following values are converted to True:

    1. 'true'
    2. 'yes'
    3. '1'
    4. 'y'
    5. 1

    The following values are converted to False:

    1. 'false'
    2. 'no'
    3. '0'
    4. 'n'
    5. 0

    :param data: input data
    :return: boolean value of the input data
    :rtype: bool
    """
    res = None
    if data is None:
        return res
    elif isinstance(data, bool):
        res = data
    elif isinstance(data, str):
        if data.lower().strip() in ["true", "yes", "1", "y"]:
            res = True
        elif data.lower().strip() in ["false", "no", "0", "n"]:
            res = False
        else:
            res = None
    elif isinstance(data, (float, int)):
        res = bool(data)

    return res


def eu_float_string_to_float(data):
    """
    eu_float_string_to_float converts strings in EU format to floats

    :param data: string of the float in EU conventions
    :type data: str
    :return: converted float from the string
    :rtype: float
    """
    if isinstance(data, str):
        res = data.replace(".", "")
        res = res.replace(",", ".")
        try:
            res = float(res)
        except Exception as e:
            raise Exception(f"Could not convert string {data} to float: {e}")
    else:
        raise TypeError("Input data should be string")

    return res
