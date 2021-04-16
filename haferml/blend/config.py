import os
from loguru import logger
import simplejson as json


def load_config(config_path, base_folder=None):
    """
    load_config loads the config files of the project

    :param config_path: path to the config file
    :type config_path: str, optional
    """
    if config_path is None:
        raise Exception(f"config_path has not been specified...")

    if not os.path.exists(config_path):
        raise Exception(
            f"config file path {config_path} does not exist! Beware of the relative path."
        )

    logger.debug(f"Loading config from {config_path}")
    with open(config_path, "r") as fp:
        config = json.load(fp)

    if not config:
        logger.warning(f"The config is empty: {config}")

    return config


def get_config(configs, path):
    """
    Get value of the configs under specified path

    :param dict configs: input dictionary
    :param list path: path to the value to be obtained

    >>> get_config({'etl':{'raw':{'local':'data/raw', 'remote': 's3://haferml-tutorials/rideindego/marshall/data/raw'}}},['etl','raw'])
    {'local':'data/raw', 'remote': 's3://haferml-tutorials/rideindego/marshall/data/raw'}
    """

    # Construct the path
    if not isinstance(path, (list, tuple)):
        logger.warning(f"path is not list nor tuple, converting to list: {path}")
        path = [path]

    # Find the values
    res = configs.copy()
    for p in path:
        res = res[p]

    return res


def construct_paths(config, base_folder):
    """
    construct_paths reconstructs the path based on base folder

    The `local` key will be replaced with the
    """

    if not config.get("local"):
        logger.warning(f"{config} does not contain local key ")
        return config

    config_recon = {}
    config_local = config["local"]
    config_name = config.get("name")
    config_local = os.path.join(base_folder, config_local)
    config_recon["local"] = config_local
    if config_name:
        config_local_full = os.path.join(config_local, config_name)
        config_recon["file_path"] = config_local_full

    return {**config, **config_recon}
