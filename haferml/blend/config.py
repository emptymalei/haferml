from loguru import logger


def get_config(configs, path):
    """
    Get value of the configs under specified path

    :param dict configs: input dictionary
    :param list path: path to the value to be obtained

    >>> get_config({'etl':{'raw':{'local':'data/raw', 'remote': 's3://haferml-tutorials/rideindego/marshall/data/raw'}}},['etl','raw'])
    {'local':'data/raw', 'remote': 's3://haferml-tutorials/rideindego/marshall/data/raw'}
    """

    # Construct the path
    if isinstance(path, list):
        path_copy = path.copy()
    elif isinstance(path, tuple):
        path_copy = list(path).copy()
    else:
        logger.warning(f"path is not list nor tuple, converting to list: {path}")
        path_copy = [path].copy()

    # Find the values
    if len(path_copy) > 1:
        pop = path_copy.pop(0)

        try:
            return get_config(configs[pop], path_copy)
        except:
            raise Exception(f"Could not get values for key {pop}")
    elif len(path_copy) == 0:
        logger.warning("No key path specified, returning the full config...")
        return configs
