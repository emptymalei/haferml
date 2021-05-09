import os
from loguru import logger
import simplejson as json
from haferml.data.wrangle.misc import get_all_paths_in_dict as _get_all_paths_in_dict
from haferml.data.wrangle.misc import (
    update_dict_recursively as _update_dict_recursively,
)


def load_config(config_path, base_folder=None):
    """
    load_config loads the config files of the project

    :param config_path: path to the config file
    :type config_path: str, optional
    """
    if config_path is None:
        raise Exception(f"config_path has not been specified...")

    if base_folder is not None:
        config_path = os.path.join(base_folder, config_path)

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

    ```
    >>> get_config({'etl':{'raw':{'local':'data/raw', 'remote': 's3://haferml-tutorials/rideindego/marshall/data/raw'}}},['etl','raw'])
    {'local':'data/raw', 'remote': 's3://haferml-tutorials/rideindego/marshall/data/raw'}
    ```
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


class Config:
    """
    Config makes it easy to load and use config files.

    :param file_path: path to the config file. If the path is relative path, please specify the base folder.
    :type file_path: str
    :param base_folder: the base folder for our working directory, defaults to None
    :type base_folder: str, optional
    """

    def __init__(self, config, base_folder=None):

        if base_folder is not None:
            logger.info(f"Using base folder: {base_folder}")

        self.base_folder = base_folder

        if isinstance(config, str):
            self.config = load_config(config_path=config, base_folder=base_folder)
        elif isinstance(config, dict):
            self.config = config
        else:
            raise Exception(
                f"Input config is not supported, should be path or dict: {config}"
            )

        self._enhance_local_paths(self.config, base_folder=self.base_folder)

    def get(self, path):
        """
        Retrieve config for a given path down in the configs.

        ```
        conf = Config(file_path="test.json", base_folder="/tmp")
        conf.get(["etl", "raw"])
        ```

        :param path: path to the specific configurations
        :type path: list
        :return: configuration of for the specific path
        """

        config = get_config(self.config, path)

        return config

    @staticmethod
    def _enhance_local_paths(config, base_folder=None):
        """
        Appends base_folder to the local paths in the configs and also the file path if name key is present.

        :param config: dictionary of configuration.
        :type config: dict
        :param base_folder: base folder of all the artifacts, defaults to None
        :type base_folder: str, optional
        """

        all_paths = _get_all_paths_in_dict(config)

        for p in all_paths:
            if p[-1] == "local":
                p_local_value = get_config(config, p)
                p_local_parent_path = p[:-1]

                if base_folder is not None:
                    p_local_value = os.path.join(base_folder, p_local_value)
                _update_dict_recursively(
                    config, p_local_parent_path + ["local_absolute"], p_local_value
                )

                p_local_parent_value = get_config(config, p_local_parent_path)
                if "name" in p_local_parent_value:
                    p_name_value = p_local_parent_value["name"]
                    p_name_value = os.path.join(p_local_value, p_name_value)
                    _update_dict_recursively(
                        config, p_local_parent_path + ["name_absolute"], p_name_value
                    )

    def __getitem__(self, item):
        return self.get(item)

    def __str__(self) -> str:
        return f"{self.config}"
