from __future__ import annotations
from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Union, Callable, Any
from loguru import logger


class TransformBase(ABC):
    """
    TransformBase transforms a dataframe.

    This is a transformation inspired by the
    package gluonts.
    """

    @abstractmethod
    def __call__(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        """
        raise NotImplementedError("This method is not implemented yet.")

    def __add__(self, other: TransformBase) -> ConcatTransform:
        """
        """
        return ConcatTransform([self, other])


class ConcatTransform(TransformBase):
    """Concatenated transforms.

    The returned transforms inherited from the

    :param transforms: List of transforms to be concatenated
    """

    def __init__(self, transforms: List[TransformBase]):
        self.transforms = []
        for transform in transforms:
            self._update(transform)

    def _update(self, transform: Union[ConcatTransform, TransformBase]):
        if isinstance(transform, ConcatTransform):
            self.transforms.extend(transform)
        elif isinstance(transform, TransformBase):
            self.transforms.append(transform)
        else:
            raise TypeError("Expected type TransformBase or ConcatTransform")

    def __call__(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        for t in self.transforms:
            dataframe = t(dataframe)

        return dataframe


class Identity(TransformBase):
    """Returns the original dataframe

    This is useful when summing up a lot of transformations.

    For example, if I have a list of `TransformBase` transformations

    ```
    my_transformations = [transform_1, transform_2, transform_3]
    ```

    ```python
    transform = sum(my_transformations, Identity())
    ```

    `transform` will be the chained transformation.
    """

    def __init__(self):
        logger.warning("This transformation does nothing")

    def __call__(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        logger.info("Returning the original dataframe")
        return dataframe


class Shuffle(TransformBase):
    """Returns a shuffled dataframe"""

    def __call__(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        logger.info("Returning the original dataframe")
        return dataframe


class ConvertCategoricalType(TransformBase):
    """Convert a column to categorical

    :param dt_column: the original datatime column
    :param target_column: the column to write to.
    Default is to overwrite original dt_column
    """

    def __init__(self, column_name: str, target_column: Optional[str] = None):
        self.column_name = column_name
        if target_column is None:
            target_column = column_name

        self.target_column = target_column

    def __call__(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        logger.info(f"converting {self.column_name} to categorical ...")
        dataframe[self.target_column] = dataframe[self.column_name].astype("category")
        self.categories = dataframe[self.target_column].cat.categories
        dataframe[self.target_column] = dataframe[self.target_column].cat.codes
        logger.info(f"converted {self.column_name} to categorical!")

        return dataframe


class ReplaceValues(TransformBase):
    """Replace some certain values with the specified value

    ```python
    lambda_filter = lambda x: x["indicator_column"] == "bad_value"

    replace_val = ReplaceValues(
        lambda_filter = lambda_filter,
        column_to_replace = "value_a_column",
        replacement_value = np.nan
    )
    ```
    
    :param lambda_filter: a callable that specifies which row to filter
    :param column_to_replace: which column to replace values with
    :param replacement_value: the value to replace with
    """
    def __init__(
        self, lambda_filter: Callable, 
        column_to_replace: str,
        replacement_value: Optional[Any] = None
    ):
        self.lambda_filter = lambda_filter
        self.column_to_replace = column_to_replace
        self.replacement_value = replacement_value

    def __call__(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        logger.info(f"replace values in {self.column_to_replace}")
        dataframe.loc[lambda x: self.lambda_filter(x), self.column_to_replace] = self.replacement_value
        return dataframe


class AddColumnWithCondition(TransformBase):
    """Add a calculated column based on a lambda function

    ```python
    lambda_filter = lambda x: x["indicator_column"] == "bad_value"

    replace_val = ReplaceValues(
        lambda_filter = lambda_filter,
        column_to_replace = "value_a_column",
        replacement_value = np.nan
    )
    ```

    :param lambda_filter: a callable that specifies which row to filter
    :param column_to_replace: which column to replace values with
    :param replacement_value: the value to replace with
    """
    def __init__(
        self, lambda_compute: Callable, 
        target_column: str,
    ):
        self.lambda_compute = lambda_compute
        self.target_column = target_column

    def __call__(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        logger.info(f"adding column {self.target_column}")
        dataframe[self.target_column] = dataframe.apply(self.lambda_compute, axis=1)
        return dataframe


class ExpandJSONValues(TransformBase):
    """Expand values for columns containing JSON objects

    :param column_names: the columns to expand
    :param json_key: the key to extract from the JSON objects
    """

    def __init__(self, column_names: list[str], json_key: str):
        if isinstance(column_names, str):
            column_names = [column_names]
        self.column_names = column_names

        self.json_key = json_key

    def __call__(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        logger.info("Extracting from JSON values")

        return dataframe.assign(
            **{
                k: dataframe.apply(
                    lambda x: (
                        x[k].get(self.json_key) if isinstance(x[k], dict) else x[k]
                    ),
                    axis=1,
                )
                for k in self.column_names
            }
        )


class Convert2Timestamp(TransformBase):
    """Convert column to datetime"""

    def __init__(self, column_name: str):
        self.column_name = column_name

    def __call__(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        logger.info(f"Converting {self.column_name} to datetime...")
        dataframe[self.column_name] = pd.to_datetime(dataframe[self.column_name])
        return dataframe


class SortbyColumn(TransformBase):
    """Sort dataframe based on column"""

    def __init__(self, column_name: str, ascending: bool = True):
        self.column_name = column_name
        self.ascending = ascending

    def __call__(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        logger.info(f"Sorting column by {self.column_name} ...")

        return dataframe.sort_values(by=self.column_name, ascending=self.ascending)


class RollingMedian(TransformBase):
    """rolling median based on column"""

    def __init__(self, column_names: str, window_size: int, min_periods: int = 1):
        self.column_names = column_names
        self.window_size = window_size
        self.min_periods = min_periods

    def __call__(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        logger.info(f"Rolling median column by {self.column_names} ...")
        non_transformed_cols = list(set(dataframe.columns) - set(self.column_names))
        return pd.merge(
            dataframe[non_transformed_cols],
            dataframe[self.column_names]
            .rolling(self.window_size, center=False, min_periods=self.min_periods)
            .median(),
            left_index=True,
            right_index=True,
            how="left",
        )
