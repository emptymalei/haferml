## Random Forest

As an example, we will build a simple random forest model. This is only a demonstration of the package so we do not care about the performance.


```python
import datetime
import os

import category_encoders as ce
import click
import joblib
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from haferml.blend.config import Config
from haferml.model.pipeline import DataSetX, ModelSetX, ModelWorkflowX
from haferml.sync.local import prepare_folders
from haferml.sync.local import isoencode
from loguru import logger
from sklearn import metrics
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.pipeline import Pipeline

logger.info(f"Experiment started at: {datetime.datetime.now()}")
load_dotenv()


def load_data(data_path):
    if data_path.endswith(".parquet"):
        dataframe = pd.read_parquet(data_path)
    else:
        raise ValueError(f"Input path file format is not supported: {data_path}")

    return dataframe


class DataSet(DataSetX):
    """
    DataSet for the model
    """

    def __init__(self, config, base_folder):
        super(DataSet, self).__init__(config, base_folder)

        self.targets = self.config.get("targets")
        self.features = self.config.get("features")
        self.cat_cols = self.config.get("encoding", {}).get("categorical_columns")

        self.test_size = self.config.get("test_size")
        self.random_state = self.config.get("random_state")

        logger.debug(
            f"features: {self.features}\n"
            f"predict: {self.targets}\n"
            f"base folder: {self.base_folder}\n"
            f"artifacts configs: {self.artifacts}"
        )

    def _encode(self):
        self.cat_encoder = ce.BinaryEncoder(cols=self.cat_cols)
        self.cat_encoder.fit(self.X, self.y)

    def create_train_test_datasets(self, data):

        self.data = data
        logger.debug(f"length of dataset: {len(self.data)}\n")

        self.X = self.data.loc[:, self.features]
        self.y = self.data.loc[:, self.targets]

        # No information leak here as we use Binary Encoder only
        self._encode()
        self.X = self.cat_encoder.transform(self.X, self.y)

        logger.debug("Splitting dataset")
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=self.test_size, random_state=self.random_state
        )

        logger.debug(
            "Shape of train and test data:\n"
            f"X_train: {self.X_train.shape}\n"
            f"y_train: {self.y_train.shape}\n"
            f"X_test: {self.X_test.shape}\n"
            f"y_test: {self.y_test.shape}\n"
        )

        # save the train test data
        self._export_train_test_data()


class ModelSet(ModelSetX):
    """
    The core of the model including hyperparameters
    """

    def __init__(self, config, base_folder):
        super(ModelSet, self).__init__(config, base_folder)

        self.test_size = self.config.get("test_size")
        self.random_state = self.config.get("random_state")

        logger.debug(
            f"features: {self.features}\n"
            f"predict: {self.targets}\n"
            f"base folder: {self.base_folder}\n"
            f"artifacts configs: {self.artifacts}"
        )

    def create_model(self):

        logger.info("Setting up hyperparameters ...")

        logger.info("Create pipeline")
        rf = RandomForestRegressor(
            random_state=self.random_state, oob_score=False, n_jobs=-1
        )

        self.pipeline_steps = [("model", rf)]
        self.pipeline = Pipeline(self.pipeline_steps)

        logger.info("Create model with CV")
        self.model = RandomizedSearchCV(
            self.pipeline,
            cv=self.config.get("cv", {}).get("folds", 3),
            n_iter=self.config.get("cv", {}).get("n_iter", 5),
            param_distributions=self.hyperparameters,
            verbose=6,
        )

    def _set_hyperparameters(self):
        hyperparams_grid = self.config.get("hyperparameters")
        if hyperparams_grid is None:
            hyperparams_grid = self._create_hyperparameter_space()
        else:
            hyperparams_grid = {
                **(self._create_hyperparameter_space()),
                **hyperparams_grid,
            }
            logger.info(f"Using hyperparameters: \n{hyperparams_grid}")

        return hyperparams_grid

    @staticmethod
    def _create_hyperparameter_space():
        """
        _create_hyperparameter_space creates a set of hyperparameters for the random forest
        """

        # Number of trees in random forest
        # n_estimators = [int(x) for x in np.linspace(50, 150, 5)]
        n_estimators = [90, 100, 110, 120]
        # Number of features to consider at every split
        max_features = ["auto", 0.9, 0.8]
        # Maximum number of levels in tree
        # max_depth = [int(x) for x in range(10, 20, 2)]
        max_depth = [None]
        # max_depth.append(None)
        # Minimum number of samples required to split a node
        # min_samples_split = [2, 4, 6]
        min_samples_split = [2]
        # Minimum number of samples required at each leaf node
        # min_samples_leaf = [1, 2, 3]
        min_samples_leaf = [1]
        # Method of selecting samples for training each tree
        bootstrap = [True]

        # feature_selection__k = [15, 20, 25, 30, 35, 40, 45, 50]

        rf_random_grid = {
            "model__n_estimators": n_estimators,
            "model__max_features": max_features,
            "model__max_depth": max_depth,
            "model__min_samples_split": min_samples_split,
            "model__min_samples_leaf": min_samples_leaf,
            "model__bootstrap": bootstrap,
        }

        return rf_random_grid


class RandomForest(ModelWorkflowX):
    """A model to predict the duration"""

    def __init__(self, config, dataset, modelset, base_folder=os.getenv("BASE_FOLDER")):
        super(RandomForest, self).__init__(config, dataset, modelset, base_folder)
        self.name = "marshall random forest"




@click.command()
@click.option(
    "-c",
    "--config",
    type=str,
    default=os.getenv("CONFIG_FILE"),
    help="Path to config file",
)
@click.option(
    "--test/--no-test",
    type=bool,
    default=False,
    help="Flag for test",
)
def preprocess(config, test):

    base_folder = os.getenv("BASE_FOLDER")

    _CONFIG = Config(config, base_folder=base_folder)
    preprocessed_data_config = _CONFIG[["preprocessing", "dataset", "preprocessed"]]
    rf_config = _CONFIG[["model", "rf"]]

    # create folders
    prepare_folders(preprocessed_data_config["local"], base_folder=base_folder)
    prepare_folders(_CONFIG[["model", "rf", "artifacts", "model", "local"]], base_folder=base_folder)

    # load transformed data
    logger.debug(f"Loading data ...")
    df = load_data(preprocessed_data_config["name_absolute"])
    if test is True:
        df = df.sample(1000)

    # model
    logger.debug(f"Prepare modelset and dataset")
    D = DataSet(config=rf_config, base_folder=base_folder)
    M = ModelSet(config=rf_config, base_folder=base_folder)

    logger.debug(f"Assemble randomforest")
    rf = RandomForest(config=rf_config, dataset=D, modelset=M)

    logger.debug(f"Training ...")
    rf.train(df)




if __name__ == "__main__":
    preprocess()
```