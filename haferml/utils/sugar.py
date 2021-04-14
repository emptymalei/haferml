import os


def check_env(var_list):
    """
    check_env checks if the given environment variables exists
    :param var_list: list of variables to be checked
    :type definition: list
    """

    missing = []
    res = {}
    for envvar in var_list:
        envvar_val = os.getenv(envvar)
        if envvar_val is None:
            missing.append(envvar)
        res[envvar] = envvar_val

    if missing:
        raise Exception(f"Missing envs {missing}")

    return res
