import json
import os
import datetime
import numpy as np

from loguru import logger


def prepare_folders(folder_list=None, base_folder=None):
    """
    prepare_folders creates the necessary folders

    :param base_folder: base folder of the whole project
    :type base_folder: str
    :param folder_list: list of folders to create, relative to base_folder
    :type folder_list: list
    """
    if folder_list is None:
        raise Exception("Please specify the list of folder using fodler_list")

    if os.path.exists(base_folder):
        logger.info(f"Using base folder {base_folder}!")

    # prepare the model folder
    if isinstance(folder_list, (tuple, list, set)):
        pass
    elif isinstance(folder_list, str):
        logger.warning(f"Converting to list: {folder_list} to a list")
        folder = [folder_list]

    for folder in folder_list:
        folder = os.path.join(base_folder, folder)
        if not os.path.exists(folder):
            os.makedirs(folder)
            logger.info(f"created {folder}")


def isoencode(obj):
    """
    isoencode decodes many different objects such as np.bool -> regular bool.

    ```python
    with open(log_file_path, "a+") as fp:
        json.dump(self.report, fp, default=isoencode)
    ```
    """
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.int64):
        return int(obj)
    if isinstance(obj, np.float64):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)


def save_records(data_inp, output, is_flush=None, write_mode=None):
    """Save list of dicts to file. Instead of loading pandas for such a simple job, this function does the work in most cases.

    :param data_inp: dict or list of dict to be saved
    :param output: path to output file
    :is_flush: whether to flush data to file for each row written to file
    :return: None
    """

    if write_mode is None:
        write_mode = "a+"

    if is_flush is None:
        is_flush = False

    if isinstance(data_inp, list):
        data = data_inp
    elif isinstance(data_inp, dict):
        data = [data_inp]
    else:
        raise Exception("Input data is neither list nor dict: {}".format(data_inp))

    try:
        with open(output, write_mode) as fp:
            for i in data:
                json.dump(i, fp)
                fp.write("\n")
                if is_flush:
                    fp.flush()
    except Exception as ee:
        raise Exception("Could not load data to file: {}".format(ee))


def load_records(data_path_inp):
    """Load data from a line deliminated json file. Instead of loading pandas for such a simple job, this function does the work in most cases.

    :param data_path_inp: data file path
    :return: list of dicts
    """

    data = []

    with open(data_path_inp, "r") as fp:
        for line in fp:
            line = line.replace("null", ' "None" ')
            try:
                line_data = json.loads(line.strip())
            except Exception as ee:
                logger.warning("could not load ", line, "\n", ee)
            data.append(line_data)

    return data
