from loguru import logger
import os
import pandas as pd
from pandas.core import base
from haferml.blend.config import construct_paths
import joblib
import simplejson as json
from haferml.sync.local import isoencode
from haferml.model.dataset import DataSet
from haferml.model.modelset import ModelSet
from haferml.model.workflow import ModelWorkflow


class DataSetX(DataSet):
    """
    DataSetX class deals with the dataset to be used in a model


    :param config: a dictionary that contains the configurations.
    :type config: dict
    :param base_folder: working directory where all the artifacts are being perserved.
    :type base_folder: str
    """

    def __init__(self, config, base_folder):
        super(DataSetX, self).__init__(config, base_folder)

        self.targets = self.config.get("targets")
        self.features = self.config.get("features")
        self.artifacts = self.config["artifacts"]

        logger.debug(f"features: {self.features}\n" f"predict: {self.targets}")

    def create_train_test_datasets(self, dataframe):
        """
        create_train_test_datasets will create

        - self.data: the full input data right before train test split
        - self.X_train, self.y_train, self.X_test, self.y_test

        :param dataframe: the dataframe to be splitted.
        :type dataframe: pandas.DataFrame
        """

        raise Exception("create_train_test_dataset has not yet been implemented!")

    @staticmethod
    def _save_data(dataframe, destination):
        """
        `_save_data` saves the dataframe locally.

        :param dataframe: dataframe to be saved
        :type dataframe: pandas.DataFrame
        :param destination: where the data is saved
        :type destination: str
        """
        logger.info("Export test and train data")
        dataframe.to_parquet(destination)

    def _export_train_test_data(self):
        """
        _export_train_test_data saves train and test datasets
        """

        dataset_folder = construct_paths(
            self.artifacts["dataset"], base_folder=self.base_folder
        )["local"]

        ## Save the train and test datasets
        logger.info("Export test and train data")
        self._save_data(
            self.X_train, os.path.join(dataset_folder, "model_X_train.parquet")
        )

        self._save_data(
            self.X_test, os.path.join(dataset_folder, "model_X_test.parquet")
        )

        self._save_data(
            pd.DataFrame(self.y_train, columns=self.pred_cols),
            os.path.join(dataset_folder, "model_y_train.parquet"),
        )

        self._save_data(
            pd.DataFrame(self.y_test, columns=self.pred_cols),
            os.path.join(dataset_folder, "model_y_test.parquet"),
        )

        # Save dataset locally
        self._save_data(self.data, os.path.join(dataset_folder, "dataset.parquet"))


class ModelSetX(ModelSet):
    """
    The core of the model including hyperparameters.

    :param config: a dictionary that contains the configurations.
    :type config: dict
    :param base_folder: working directory where all the artifacts are being perserved.
    :type base_folder: str
    """

    def __init__(self, config, base_folder):
        super(ModelSet, self).__init__(config, base_folder)

        self.targets = self.config.get("targets")
        self.features = self.config.get("features")
        self.artifacts = self.config["artifacts"]

        logger.debug(f"features: {self.features}\n" f"predict: {self.targets}")

    def create_model(self):
        ...

    @property
    def hyperparameters(self):
        return self._set_hyperparameters()

    def _set_hyperparameters(self):
        """
        _set_hyperparameters creates hyperpamater grid
        """
        ...


class ModelWorkflowX(ModelWorkflow):
    """ModelWorkflowX class that holds DataSetX and ModelSetX

    :param config: a dictionary that contains the configs.
    :type config: dict
    :param dataset: a DataSet object that contains the data and provides a `create_train_test_datasets` method.
    :type dataset: haferml.model.DataSet
    :param modelset: a ModelSet object that contains the model as well as the hyperparameters and a `create_model`.
    :type modelset: haferml.model.ModelSet
    :param base_folder: working directory where all the artifacts are being perserved.
    :type base_folder: str
    """

    def __init__(self, config, dataset, modelset, base_folder):
        self.config = config
        self.base_folder = base_folder
        self.DataSet = dataset
        self.ModelSet = modelset
        self.artifacts = self.config["artifacts"]

    def fit_and_report(self):
        """
        _fit_and_report fits the model using input data and generate reports
        """

        logger.info("Fitting the model ...")
        logger.debug(
            "Shape of train data:\n"
            f"X_train: {self.DataSet.X_train.shape}, {self.DataSet.X_train.sample(3)}\n"
            f"y_train: {self.DataSet.y_train.shape}, {self.DataSet.y_train.sample(3)}"
        )
        self.ModelSet.model.fit(
            self.DataSet.X_train.squeeze(), self.DataSet.y_train.squeeze()
        )

        self.report = {
            "hyperparameters": self.ModelSet.hyperparams_grid,
            "best_params": self.ModelSet.model.best_params_,
            "cv_results": self.ModelSet.model.cv_results_,
        }

        logger.debug(self.report)

    def export_results(self):
        """
        export_results saves the necessary artifacts
        """
        model_artifacts = construct_paths(
            self.artifacts["model"], base_folder=self.base_folder
        )
        model_folder = model_artifacts["local"]
        model_path = model_artifacts["file_path"]

        if not os.path.exists(model_folder):
            os.makedirs(model_folder)

        logger.info("Preserving models ...")
        joblib.dump(self.ModelSet.model, model_path)

        logger.info("Perserving logs ...")
        log_file_path = f"{model_path}.log"
        logger.info(f"Save log file to {log_file_path}")
        with open(log_file_path, "a+") as fp:
            json.dump(self.report, fp, default=isoencode)
            fp.write("\n")
        logger.info(f"Saved logs")

    def train(self, dataset):
        """
        train connects the training workflow

        :param dataset: dataframe being used to train the model
        :type dataset: pandas.DataFrame
        """

        logger.info("1. Create train test datasets")
        self.DataSet.create_train_test_datasets(dataset)
        logger.info("2. Create model")
        self.ModelSet.create_model()
        logger.info("3. Fit model and report")
        self.fit_and_report()
        logger.info("4. Export results")
        self.export_results()
