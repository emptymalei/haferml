from loguru import logger
from urllib.parse import unquote as _unquote
from .consts import ELF_CODE as _ELF_CODE


def clean_company_name(
    company_name,
    remove_chars=None,
    chars_data=None,
    remove_legal_form=None,
    legal_form_data=None,
    company_name_map=None,
):
    """Clean company name by removing unnecessary strings.

    1. Remove some special characters.
    2. Strip the whitespaces.
    3. Remove legal forms such as gmbh, e.v.
    """
    if not isinstance(company_name, str):
        logger.warning(
            "clean_company_name:: input company is not string: {}".format(company_name)
        )
    logger.debug(f"clean_company_name:: company_name is {company_name}")

    if legal_form_data:
        remove_legal_form = True
    if remove_legal_form is None:
        remove_legal_form = False

    if legal_form_data and (legal_form_data is None):
        legal_form_data = _ELF_CODE

    if chars_data:
        remove_chars = True
    if remove_chars is None:
        remove_chars = False
    if remove_chars and (chars_data is None):
        chars_data = ['"']

    # unquote name to make sure the string do not have url encodings
    logger.debug(f"clean_company_name:: unquoting {company_name}")
    company_name = _unquote(company_name)

    company_name = company_name.strip()

    first_three_characters_forbiden = ("*", "=", "#", "%", "+")
    company_name_first_three = company_name[:3]
    company_name_fourth_to_last = company_name[3:]
    for i in first_three_characters_forbiden:
        company_name_first_three = company_name_first_three.replace(i, "")
    company_name = company_name_first_three + company_name_fourth_to_last
    company_name = company_name.strip()

    if remove_legal_form:
        logger.debug(f"clean_company_name:: legalform for {company_name}")
        for elf in legal_form_data:
            spaced_elf = " " + elf
            if company_name.endswith(spaced_elf):
                logger.debug(f"Removing {elf} from company name {company_name}")
                company_name = company_name[: -len(spaced_elf)]

        company_name = company_name.strip()

    if remove_chars:
        # remove special characters from company name
        for char in chars_data:
            company_name = company_name.replace(char, "")

    # convert to lower case
    company_name = company_name.lower()

    logger.debug(f"clean_company_name:: company_name_enforcement for {company_name}")
    # Rename companies using a pre-defined map
    if company_name_map:
        logger.debug(
            "company_data::looked through company name enforcement: {}".format(
                company_name_map
            )
        )
        if company_name_map:
            company_name = company_name_map.get("company")
            logger.debug(f"company_data::company_name_map exists: {company_name}")

    return company_name
