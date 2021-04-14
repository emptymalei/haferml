import pandas as pd
from haferml.data.preprocessing.ingredients import attributes
from haferml.data.preprocessing.pipeline import BasePreProcessor


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
