import pandas as pd
from haferml.preprocess.ingredients import OrderedProcessor, attributes
from loguru import logger


class BasePreProcessor(OrderedProcessor):
    """
    Shared methods to transform the datasets

    The following example demonstrates how to use it.

    ```python
    from haferml.data.preprocessing.ingredients import OrderedProcessor, attributes

    class DemoPreProcessor(BasePreProcessor):
        def __init__(self, config, columns, cutoff_timestamp=None):
            super(DemoPreProcessor, self).__init__(
                config=config, columns=columns
            )

            self.cutoff_timestamp=cutoff_timestamp

        def merge_datasets(self, datasets):

            df_a = datasets["a"]
            df_b = datasets["b"]

            # 1. We only take data that is later than a certain date

            if self.cutoff_timestamp:
                filter_a_mask = (
                    df_a.req_created_at > self.cutoff_timestamp
                )

            df_a = df_a.loc[filter_a_mask]

            # combine dataset a and b
            dataset = pd.merge(
                df_a,
                df_b,
                how="left",
                on="request_id",
            )

            return dataset

        @attributes(order=1)
        def _fix_names(self, dataset):

            dataset["names"] = dataset.names.replace(
                "Tima", "Tim"
            )

        @attributes(order=2)
        def _convert_requirement_to_bool(self, dataset):

            dataset[
                "requirements"
            ] = dataset.requirements.apply(
                lambda x: False if pd.isnull(x) else True
            )

        @attributes(order=12)
        def _filter_columns_and_crossing(self, dataset):
            # _filter_columns_and_crossing removes unnecessary columns and append crossings

            # only keep the specified columns
            # the following code also deals with feature crossings
            if self.columns:
                columns = list(set(self.columns))
                crossing = []
                features_ex = []
                for col in columns:
                    if "__" in col:
                        crossing.append(col)
                    else:
                        features_ex.append(col)

                dataset = dataset[features_ex]

                for fc in crossing:
                    fc_cols = fc.split("__")
                    fc_series = dataset[fc_cols[0]]
                    for fc_col in fc_cols[1:]:
                        fc_series = fc_series * dataset[fc_col]
                    dataset[fc] = fc_series


    dp = DemoPreProcessor(config={}, columns=['names', 'requirements', 'names__requirements'])
    dataset = {
        "a": pd.DataFrame([{"names": "Tima Cook", "requirements": "I need it"}]),
        "b": pd.DataFrame([{"names": "Time Cook", "requirements": None}])
    }
    dp.preprocess(dataset)
    ```
    """

    def __init__(self, config, columns):
        super(BasePreProcessor, self).__init__(config=config, columns=columns)

        self.config = self.params.get("config")
        logger.info(f"Applying config:\n{self.config}")
        self.columns = self.params.get("columns")
        logger.info(f"Applying columns:\n{self.columns}")

    def merge_datasets(self, datasets):
        """
        merge_datasets merges the datasets into one singular dataframe to be processed.

        :param datasets: dictionary that contains the dataframes
        :type datasets: dict
        """

        raise NotImplementedError("Please implement this method!")

    def preprocess(self, datasets, **params):
        """
        preprocess connects the transforms into pipelines

        :param datasets: input datasets as list or dict of single dataframe
        :param merge: whether and how to merge datasets: True or False
        """

        if params.get("merge") is True:
            dataframe = self.merge_datasets(datasets)
        elif isinstance(datasets, dict):
            logger.warning(
                "No specific merge methods specified\n"
                "Auto concating all the datasets"
            )
            dataframe = pd.concat(datasets.values())
        elif isinstance(datasets, list):
            logger.warning(
                "No specific merge methods specified\n"
                "Auto concating all the datasets"
            )
            dataframe = pd.concat(datasets)
        elif isinstance(datasets, pd.DataFrame):
            logger.info(
                "Input dataset is a single dataframe, " "making a copy for safety"
            )
            dataframe = datasets.copy()
        else:
            raise TypeError("Input datasets should be dataframe or list of dataframes")

        # Go through the transforms
        for t in self.transforms:
            logger.info(f"Performing {t} ...")
            self.transforms[t](dataframe)
            logger.info(f"{t} is done.")

        return dataframe


if __name__ == "__main__":

    from haferml.preprocess.ingredients import attributes

    class DemoPreProcessor(BasePreProcessor):
        def __init__(self, config, columns, cutoff_timestamp=None):
            super(DemoPreProcessor, self).__init__(config=config, columns=columns)

            self.cutoff_timestamp = cutoff_timestamp

        def merge_datasets(self, datasets):
            """
            merge_datasets merges the dataframes in the datasets
            """
            df_a = datasets["a"]
            df_b = datasets["b"]

            # 1. We only take data that is later than a certain date

            if self.cutoff_timestamp:
                filter_a_mask = df_a.req_created_at > self.cutoff_timestamp

            df_a = df_a.loc[filter_a_mask]

            # combine dataset a and b
            dataset = pd.merge(
                df_a,
                df_b,
                how="left",
                on="request_id",
            )

            return dataset

        @attributes(order=1)
        def _fix_names(self, dataset):

            dataset["names"] = dataset.names.replace("Tima", "Tim")

        @attributes(order=2)
        def _convert_requirement_to_bool(self, dataset):

            dataset["requirements"] = dataset.requirements.apply(
                lambda x: False if pd.isnull(x) else True
            )

        @attributes(order=12)
        def _filter_columns_and_crossing(self, dataset):
            """
            _filter_columns_and_crossing removes unnecessary columns and append crossings
            """

            # only keep the specified columns
            # the following code also deals with feature crossings
            if self.columns:
                columns = list(set(self.columns))
                crossing = []
                features_ex = []
                for col in columns:
                    if "__" in col:
                        crossing.append(col)
                    else:
                        features_ex.append(col)

                dataset = dataset[features_ex]

                for fc in crossing:
                    fc_cols = fc.split("__")
                    fc_series = dataset[fc_cols[0]]
                    for fc_col in fc_cols[1:]:
                        fc_series = fc_series * dataset[fc_col]
                    dataset[fc] = fc_series

    dp = DemoPreProcessor(
        config={}, columns=["names", "requirements", "names__requirements"]
    )
    dataset = {
        "a": pd.DataFrame([{"names": "Tima Cook", "requirements": "I need it"}]),
        "b": pd.DataFrame([{"names": "Time Cook", "requirements": None}]),
    }
    dp.preprocess(dataset)
