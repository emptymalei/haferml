## Preprocessing

Preprocessing is using ordered member function by inheriting from `BasePreProcessor`.


```python
import datetime
import os

import click
import pandas as pd
import simplejson as json
from dotenv import load_dotenv
from haferml.blend.config import Config
from haferml.preprocess.ingredients import attributes
from haferml.preprocess.pipeline import BasePreProcessor
from haferml.sync.local import prepare_folders
from loguru import logger

logger.info(f"Experiment started at: {datetime.datetime.now()}")
load_dotenv()


def load_data(data_path):
    if data_path.endswith(".parquet"):
        dataframe = pd.read_parquet(data_path)
    else:
        raise ValueError(f"Input path file format is not supported: {data_path}")

    return dataframe


class Preprocess(BasePreProcessor):
    """
    Preprocess dataset
    There is very little to preprocess in this example. But we will keep this class for illustration purpose.
    """

    def __init__(self, config):
        super(Preprocess, self).__init__(config=config)
        self.feature_cols = self.config["features"]
        self.target_cols = self.config["targets"]

    @attributes(order=1)
    def _drop_unused_columns(self, dataframe):

        self.dataframe = dataframe[self.feature_cols + self.target_cols]

        return self.dataframe



@click.command()
@click.option(
    "-c",
    "--config",
    type=str,
    default=os.getenv("CONFIG_FILE"),
    help="Path to config file",
)
def preprocess(config):

    base_folder = os.getenv("BASE_FOLDER")

    _CONFIG = Config(config, base_folder=base_folder)

    preprocessed_data_config = _CONFIG[["preprocessing", "dataset", "preprocessed"]]
    transformed_trip_data_config = _CONFIG[["etl", "transformed", "trip_data"]]

    # create folders
    prepare_folders(preprocessed_data_config["local"], base_folder=base_folder)
    prepare_folders(transformed_trip_data_config["local"], base_folder=base_folder)

    # load transformed data
    df = load_data(transformed_trip_data_config["name_absolute"])

    # preprocess
    pr = Preprocess(config=_CONFIG[["preprocessing"]])
    df = pr.run(df)

    # save
    df.to_parquet(preprocessed_data_config["name_absolute"], index=False)
    logger.info(f'Saved preprocessed data to {preprocessed_data_config["name_absolute"]}')

    return df


if __name__ == "__main__":
    preprocess()
```