import json
from typing import Literal, Optional

from cloudpathlib import AnyPath
from loguru import logger
from pydantic import (
    BaseModel,
    ConfigDict,
    computed_field,
    field_serializer,
    model_validator,
)
from typing_extensions import Self



class TrainConfig:
    """Train config

    :param config_path: path to config file
    """

    def __init__(self, config_path: AnyPath):
        self.config_path = config_path

    def init(self) -> None:
        with open(self.config_path, "w") as fp:
            json.dump({}, fp, indent=4)

    @property
    def config(self) -> dict:
        with open(self.config_path, "r") as fp:
            config = json.load(fp)

        return config

    def save(self, config: dict) -> None:
        with open(self.config_path, "w") as fp:
            json.dump(config, fp, indent=4)

    def save_as(self, path: AnyPath) -> None:
        with path.open("w") as fp:
            logger.debug(f"saving config as {path}...")
            json.dump(self.config, fp, indent=4)

    def update(self, data: dict, return_value: bool = False) -> dict:
        """Add new info to config"""
        config = self.config
        new_config = {**config, **data}

        self.save(new_config)

        return new_config


class DatasetConfig(BaseModel):
    """
    Configs for datasets.

    This config specifies a dataset.

    We assume that a dataset lies inside a folder,
    with data and metadata lies in subfolders.

    :param dataset_base_path: folder path to the dataset
    """

    prefix: str
    timestamp: str
    dataset_base_path: AnyPath
    data_relative_path: str
    metadata_relative_path: str
    check_existing: bool = True
    stats: Optional[dict] = {}

    @computed_field  # type: ignore[misc]
    @property
    def data_path(self) -> AnyPath:
        return self.dataset_base_path / self.data_relative_path

    @computed_field  # type: ignore[misc]
    @property
    def metadata_path(self) -> AnyPath:
        return self.dataset_base_path / self.metadata_relative_path

    @computed_field  # type: ignore[misc]
    @property
    def metadata(self) -> dict:
        metadata = {}
        if self.check_existing:
            with self.metadata_path.open("r") as fp:
                metadata = json.load(fp)

        return metadata

    @model_validator(mode="after")
    def check_file_exists(self) -> Self:

        if self.check_existing:
            if not self.metadata_path.exists():
                raise FileNotFoundError(
                    f"metadata_path={self.metadata_path} doesn't exist."
                )

            if not self.data_path.exists():
                raise FileNotFoundError(f"data_path={self.data_path} doesn't exist.")

        return self

    @field_serializer("dataset_base_path", "data_path", "metadata_path")
    def serialize_anypath(self, value: AnyPath, _info):
        return str(value)


class TuningConfig(BaseModel):
    """Hyperparameter tuning config"""

    study_name: str
    objective_metric: str
    objective_direction: Literal["minimize", "maximize"]
    objecctive_agg: Literal["minimum", "maximum", "mean", "median", "minimize"]

    optuna_storage: AnyPath | str
    load_if_exists: bool = False


class TuningStudy(BaseModel):
    """Study result of the hyper parameter tuning"""

    best_value: float | int
    best_params: dict
    best_trial: str
    trials: list[dict]


class ModelMeta(BaseModel):
    """Model information"""

    model: str
    model_type: Optional[str] = None
    encoder: Optional[str] = None
    scaler: Optional[str] = None
    numerical_columns: list[str]
    categorical_columns: list[str]
    features: list[str]
    model_input_feature_names: list[str]
    targets: list[str]
    metrics: dict
    model_path: Optional[AnyPath] = None
    model_meta_path: Optional[AnyPath] = None

    @field_serializer(
        "model_path",
        "model_meta_path",
    )
    def serialize_anypath(self, value: AnyPath, _info):
        return str(value)


class ModelEvaluation(BaseModel):
    """Evaluations of the model"""

    metrics: dict
    eval_raw_dataset_config: Optional[DatasetConfig] = None
    eval_preprocessed_dataset_config: Optional[DatasetConfig] = None
    model_meta: Optional[ModelMeta] = None
    metrics_raw_data_path: Optional[AnyPath] = None

    @field_serializer(
        "metrics_raw_data_path",
    )
    def serialize_anypath(self, value: AnyPath, _info):
        return str(value)


class ExperimentConfig(BaseModel):
    """Configs for an experiment

    :param base_folder:
    """

    model_config = ConfigDict(extra="allow")

    base_folder: AnyPath
    experiment_timestamp: str

    prefix: Optional[str] = None

    raw_dataset_config: Optional[DatasetConfig] = None
    preprocessed_dataset_config: Optional[DatasetConfig] = None

    eval_raw_dataset_config: Optional[DatasetConfig] = None
    eval_preprocessed_dataset_config: Optional[DatasetConfig] = None

    monitoring_raw_dataset_config: Optional[DatasetConfig] = None
    monitoring_preprocessed_dataset_config: Optional[DatasetConfig] = None

    pre_params: Optional[BaseModel] = None
    preprocessing_uses_sample: Optional[bool] = None
    preprocessed_samples: Optional[int] = None

    hyperparam_tuning_config: Optional[TuningConfig] = None
    hyperparam_tuning_results: Optional[TuningStudy] = None

    model_str: Optional[str] = None

    experiment_id: Optional[str] = None

    description: str = ""

    @computed_field  # type: ignore[misc]
    @property
    def config_path(self) -> AnyPath:
        return (
            self.base_folder / "configs" / self.experiment_id / "experiment_config.json"
        )

    @computed_field  # type: ignore[misc]
    @property
    def raw_path(self) -> AnyPath:
        return (
            self.base_folder / "configs" / self.experiment_id / "experiment_config.json"
        )

    @computed_field  # type: ignore[misc]
    @property
    def default_raw_data_parent_folder(self) -> AnyPath:
        return self.base_folder / "datasets" / "raw" / self.prefix

    @computed_field  # type: ignore[misc]
    @property
    def default_raw_data_folder(self) -> AnyPath:
        return (
            self.base_folder
            / "datasets"
            / "raw"
            / self.prefix
            / self.experiment_id
        )

    @computed_field  # type: ignore[misc]
    @property
    def default_preprocessed_data_parent_folder(self) -> AnyPath:
        return self.base_folder / "datasets" / "preprocessed" / self.prefix

    @computed_field  # type: ignore[misc]
    @property
    def default_preprocessed_data_folder(self) -> AnyPath:
        return (
            self.base_folder
            / "datasets"
            / "preprocessed"
            / self.prefix
            / self.experiment_id
        )

    @computed_field  # type: ignore[misc]
    @property
    def model_artifacts_folder(self) -> AnyPath:
        model_artifacts_folder = self.base_folder / "artifacts" / self.experiment_id
        if not model_artifacts_folder.exists():
            model_artifacts_folder.mkdir()

        return model_artifacts_folder

    @model_validator(mode="after")
    def check_experiment_id(self) -> Self:
        if self.experiment_id is None:
            self.experiment_id = (
                f"{self.prefix}_{self.experiment_timestamp}"
            )

        return self

    @field_serializer(
        "base_folder",
        "config_path",
        "raw_path",
        "default_raw_data_parent_folder",
        "default_raw_data_folder",
        "default_preprocessed_data_parent_folder",
        "default_preprocessed_data_folder",
        "model_artifacts_folder",
    )
    def serialize_anypath(self, value: AnyPath, _info):
        return str(value)

    @classmethod
    def load_from_json(cls, base_folder: AnyPath, experiment_id: str) -> AnyPath:
        config_path = base_folder / "configs" / experiment_id / "experiment_config.json"

        with config_path.open("r") as fp:
            config = json.load(fp)

        return cls.model_validate(config)
