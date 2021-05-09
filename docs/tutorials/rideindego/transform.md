## Transform

The zip files from the previous step ([Extract](../extract)) are cleaned up and saved as one data file using `TripDataCleansing`.




=== "Pipeline"

    ```python
    import os

    import click
    import pandas as pd
    import simplejson as json
    from dotenv import load_dotenv
    from haferml.blend.config import Config
    from haferml.sync.local import prepare_folders
    from loguru import logger

    from utils.transformer import TripDataCleansing
    from utils.transformer import get_all_raw_files
    from utils.transformer import load_data

    load_dotenv()


    @click.command()
    @click.option(
        "-c",
        "--config",
        type=str,
        default=os.getenv("CONFIG_FILE"),
        help="Path to config file",
    )
    def transform(config):

        base_folder = os.getenv("BASE_FOLDER")

        _CONFIG = Config(config, base_folder=base_folder)

        etl_trip_data_config = _CONFIG[["etl", "raw", "trip_data"]]
        transformed_trip_data_config = _CONFIG[["etl", "transformed", "trip_data"]]

        # create folders
        prepare_folders(etl_trip_data_config["local"], base_folder)
        prepare_folders(transformed_trip_data_config["local"], base_folder)

        # load raw data
        raw_data_files = get_all_raw_files(etl_trip_data_config["local_absolute"])
        dataset = load_data(raw_data_files)

        # data cleansing
        logger.info("Cleaning up data")
        cleaner = TripDataCleansing(
            config=_CONFIG,
            target_local=transformed_trip_data_config["name_absolute"],
        )
        cleaner.run(dataset)
        logger.info("Saved clean data: {}".format(cleaner.target_local))


    if __name__ == "__main__":
        transform()
    ```

=== "TripDataCleansing"

    ```python
    import datetime
    import os

    import numpy as np
    import pandas as pd
    from loguru import logger
    from haferml.preprocess.pipeline import BasePreProcessor, attributes


    class TripDataCleansing(BasePreProcessor):
        """Load, transform, and Dump trip data"""

        def __init__(self, config, **params):
            super(TripDataCleansing, self).__init__(
                config=config,
                **params
            )

        @attributes(order=1)
        def _datetime_transformations(self, dataframe):
            """Standardize datetime formats"""

            # extract date from datetime strings
            # they have different formats for dates so it is easier to
            # use pandas
            self.dataframe = dataframe
            self.dataframe["date"] = self.dataframe.start_time.apply(
                lambda x: x.split(" ")[0] if x else None
            )
            self.dataframe["date"] = pd.to_datetime(self.dataframe.date)

            # extract hour of the day
            # there exists different time formats
            self.dataframe["hour"] = self.dataframe.start_time.apply(
                lambda x: int(float(x.split(" ")[-1].split(":")[0]))
            )

            # get weekday
            self.dataframe["weekday"] = self.dataframe.date.apply(lambda x: x.weekday())

            # get month
            self.dataframe["month"] = self.dataframe.date.apply(lambda x: x.month)

        @attributes(order=2)
        def _duration_normalization(self, dataframe):
            """Duration was recorded as seconds before 2017-04-01.
            Here we will normalized durations to minutes
            """

            df_all_before_2017q1 = self.dataframe.loc[
                self.dataframe.date < pd.to_datetime(datetime.date(2017, 4, 1))
            ]
            df_all_after_2017q1 = self.dataframe.loc[
                self.dataframe.date >= pd.to_datetime(datetime.date(2017, 4, 1))
            ]

            df_all_before_2017q1["duration"] = df_all_before_2017q1.duration / 60

            self.dataframe = pd.concat([df_all_before_2017q1, df_all_after_2017q1])

        @attributes(order=3)
        def _backfill_bike_types(self, dataframe):
            """Bike types did not exist until q3 of 2018
            because they only had standard before this.
            """

            self.dataframe["bike_type"] = self.dataframe.bike_type.fillna("standard")

        @attributes(order=4)
        def _fill_station_id(self, dataframe):
            """start_station_id has null values
            fillna with 0 for the station id
            """
            self.dataframe["start_station_id"].fillna(0, inplace=True)

        @attributes(order=5)
        def _normalize_coordinates(self, dataframe):
            """Bike coordinates have diverging types: str or float, normalizing to float"""

            def convert_to_float(data):
                try:
                    return float(data)
                except Exception:
                    logger.debug(f"Can not convert {data}")
                    return np.nan

            self.dataframe["start_lat"] = self.dataframe.start_lat.apply(convert_to_float)
            self.dataframe["start_lon"] = self.dataframe.start_lon.apply(convert_to_float)
            self.dataframe["end_lat"] = self.dataframe.end_lat.apply(convert_to_float)
            self.dataframe["end_lon"] = self.dataframe.end_lon.apply(convert_to_float)

        @attributes(order=6)
        def _normalized_bike_id(self, dataframe):
            """
            _normalized_bike_id bike_id can be str or int or float
            not all ids can be converted to int so we will use str
            """

            self.dataframe["bike_id"] = self.dataframe.bike_id.apply(str)

        @attributes(order=7)
        def _save_all_trip_data(self, dataframe):
            """Dump all trip data to the destination define in config"""

            logger.debug(self.dataframe.sample(10))
            self.target_local = self.params["target_local"]

            try:
                if self.target_local.endswith(".parquet"):
                    self.dataframe.to_parquet(self.target_local, index=False)
                elif self.target_local.endswith(".csv"):
                    self.dataframe.to_csv(self.target_local, index=False)
                else:
                    raise ValueError(
                        f"Specified target_local is not valid (should be .csv or .parquet):{self.target_local}"
                    )
            # TODO: should be more specific about the exceptions
            except Exception as ee:
                raise Exception(f"Could not save data to {self.target_local}")

    ```