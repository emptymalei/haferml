from loguru import logger
import re


def data_validator(input_str, validate_type):
    """
    data_validator is an object that hosts several validators for different
    types of data such as domain name, email address, etc.

    The inputs are mostly validated using regex.

    :param input_str: input string to be validated
    :type input_str: str
    :param validate_type: the type of data to be validated against
    :type validate_type: str
    """

    regex_validate_types = {
        "domain": re.compile(
            r"^(?:[a-z0-9]"  # First character of the domain
            r"(?:[a-z0-9-_]{0,61}[a-z0-9])?\.)"  # Sub domain + hostname
            r"+[a-z0-9][a-z0-9-_]{0,61}"  # First 61 characters of the gTLD
            r"[a-z0-9]$"  # Last character of the gTLD
        ),
        "email": re.compile(
            r"^(?:[a-z0-9]"  # First character of the domain
            r"(?:[a-z0-9-_]{0,61}[a-z0-9])?\.)"  # Sub domain + hostname
            r"+[a-z0-9][a-z0-9-_]{0,61}"  # First 61 characters of the gTLD
            r"[a-z0-9]$"  # Last character of the gTLD
        ),
    }

    if validate_type not in regex_validate_types:
        raise ValueError(f"validate_type ({validate_type}) is not defined")
    else:
        matched = regex_validate_types.get(validate_type).match(input_str)
        if matched:
            return True
        else:
            return False
