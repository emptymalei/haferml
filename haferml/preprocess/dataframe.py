from __future__ import annotations
import abc
import pandas as pd
from typing import List, Optional
from loguru import logger


class DFTransform(abc.ABC):
    """abstract class for DataFrame transformations"""

    @abc.abstractmethod
    def __call__(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        pass

    def chain(self, other: DFTransform) -> Chain:
        return Chain([self, other])

    def __add__(self, other: DFTransform) -> Chain:
        return self.chain(other)


class Chain(DFTransform):
    """Chain multiple transformations together

    :param transformations: list of `DFTransform` to be iterated over
    """

    def __init__(self, transformations: list[DFTransform]):
        self.transformations: List[DFTransform] = []
        for transformation in transformations:
            if isinstance(transformation, Chain):
                self.transformations.extend(transformation.transformations)
            elif isinstance(transformation, DFTransform):
                self.transformations.append(transformation)
            else:
                raise TypeError(
                    f"Expected DFTransform or Chains, got {type(transformation)}"
                )

    def __call__(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        for t in self.transformations:
            dataframe = t(dataframe)
        return dataframe


class Identity(DFTransform):
    """Returns the original dataframe

    This is useful when summing up a lot of transformations.

    For example, for a given list of `DFTransform`,

    ```python
    transformations = [t_1, t_2, t_3]
    ```

    we can use `sum` to concat them,

    ```python
    transform = sum(transformations, Identity())
    ```
    """

    def __init__(self):
        logger.debug("This transformation does nothing.")

    def __call__(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        logger.debug("Returning the original dataframe")
        return dataframe


class ConvertCategoricalType(DFTransform):
    """Convert a column to categorical

    :param column_name: name of the original column
    :param target_column: name of the new column
    """

    def __init__(self, column_name: str, target_column: Optional[str] = None):
        self.column_name = column_name
        if target_column is None:
            target_column = column_name
        self.target_column = target_column

    def __call__(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        logger.debug(f"Converting {self.column_name} to categorical")
        dataframe[self.target_column] = dataframe[self.column_name].astype("category")
        self.categories = dataframe[self.target_column].cat.categories
        dataframe[self.target_column] = dataframe[self.target_column].cat.codes

        return dataframe


class ExpandJSONValues(DFTransform):
    """Create tabular form from JSON values

    :param column_names: list of column names to be expanded
    """

    def __init__(
        self, column_names: list[str], json_key: str, target_column_prefix: str = ""
    ):
        if isinstance(column_names, str):
            column_names = [column_names]
        self.column_names = column_names
        self.json_key = json_key
        self.target_column_prefix = target_column_prefix

    def __call__(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        logger.debug(f"Expanding JSON values from {self.column_names}")
        return dataframe.assign(
            **{
                f"{self.target_column_prefix}_{k}_{self.json_key}": dataframe.apply(
                    lambda x: x[self.json_key].get(k), axis=1
                )
                for k in self.column_names
            }
        )
