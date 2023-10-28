from __future__ import annotations
from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Union


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
