import inspect
import re
import time

import haferml.data.wrangling as wlg
import pandas as pd
from loguru import logger


class Transformer:
    """
    Base Transformer of a single data record
    """

    def __init__(self, schema, use_schema_column=None):

        if use_schema_column is None:
            use_schema_column = "source_column"
        self.use_schema_column = use_schema_column
        # specify the schema content to use
        self.schema = schema
        self._schema_to_utils()

        # get current timestamp
        self.current_timestamp = int(time.time())

    def _schema_to_utils(self):
        """
        _schema_to_utils converts some utility schemas using the input full schema
        """
        self.column_rename_schema = {
            i.get("column_name"): i.get("column_name") for i in self.schema
        }

        # build transformer schema
        self.transformer_schema = {
            i.get("column_name"): {"type": i.get("type")} for i in self.schema
        }
        self._get_transformers()  # enhances the schema with the transformer function

    def _get_transformers(self):
        """
        _get_transformers extracts the list of transformers
        """
        re_transformer_name = re.compile("^_transformer__(.*?)$")

        transformers = {}
        all_methods = dict(inspect.getmembers(self))
        for i in all_methods:
            if i.startswith("_transformer__"):
                transformer_name = re_transformer_name.findall(i)[0]
                transformer_method_i = all_methods.get(i)
                transformers[transformer_name] = transformer_method_i

        logger.debug("All methods: {}".format(all_methods))
        logger.info("All predefined transformers: {}".format(transformers))

        for i in self.transformer_schema:
            logger.info("this transformer schema: {}".format(i))
            i_val = self.transformer_schema.get(i, {})
            if i in transformers:
                i_val["transformer"] = transformers.get(i)
                logger.info("Has predefined transformer for {}".format(i))
            else:
                logger.info(
                    "Using default transformer for {}; format: {}".format(
                        i, i_val.get("type")
                    )
                )
                to_format_type = i_val.get("type")
                i_val["transformer"] = self._universal_transformer(
                    to_format=to_format_type
                )

            self.transformer_schema[i] = i_val

    @staticmethod
    def _universal_transformer(to_format, from_format=None):
        """
        _general_transformer is to be used if a specific transformer of the column is not found
        """

        def transformer(data):
            """
            transformer is the actual transformer
            """
            if pd.isnull(data):
                return None

            logger.debug(f"Transforming {data} to format {to_format}")
            if to_format.lower() in ("str", "string"):
                try:
                    res = str(data)
                    res = res.strip()
                except Exception as e:
                    raise Exception("Could not convert {} to str".format(data))
            elif to_format.lower() == "int":
                if isinstance(data, str):
                    if ("." in data) or ("," in data):
                        data = wlg.misc.eu_float_string_to_float(data)
                try:
                    res = int(float(data))
                except Exception as e:
                    raise Exception("Could not convert {} to float->int".format(data))
            elif to_format.lower() == "float":
                if isinstance(data, str):
                    if ("." in data) or ("," in data):
                        data = wlg.misc.eu_float_string_to_float(data)
                try:
                    res = float(data)
                except Exception as e:
                    raise Exception("Could not convert {} to float".format(data))
            elif to_format.lower() == "datetime":
                res = wlg.datetime.convert_to_datetime(data, dayfirst=False)
            elif to_format.lower() == "date":
                res = wlg.datetime.convert_to_date(data)
            elif to_format.lower() == "bool":
                res = wlg.misc.convert_to_bool(data)
            elif to_format.lower() == "list":
                res = wlg.misc.convert_str_repr_to_list(data)
            else:
                raise Exception(
                    f"Can not transform {data}; No transformer defined for the format: {to_format}"
                )

            return res

        return transformer

    def transform(self, record):
        """
        transform transforms the json (list of dict data) into standardized format
        """

        # sometime the transformations requires other fields
        # we need to set self.record to access all the fields
        self.record = record.copy()
        try:
            for key, val in record.items():
                try:
                    val = self.transformer_schema[key]["transformer"](val)
                    record[key] = val
                except Exception as e:
                    logger.error(
                        "Failed to transform key, val: {}, {}; schema is {}; e {}".format(
                            key, val, self.transformer_schema[key], e
                        )
                    )
        except Exception as e:
            raise Exception(
                "Failed to transform record: {};error is {}".format(record, e)
            )

        return record
