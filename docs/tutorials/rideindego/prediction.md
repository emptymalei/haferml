## Prediction

To use the model, we will reload the model from the artifacts saved in the training step. It's very easy to reload the model, e.g., `ModelSet` in the following example.


```python
import os

import click
import joblib
import pandas as pd
from dotenv import load_dotenv
from haferml.blend.config import Config
from haferml.model.pipeline import ModelSetX
from haferml.sync.local import prepare_folders
from loguru import logger

load_dotenv()


class ModelSet(ModelSetX):
    """
    The core of the model including hyperparameters
    """

    def __init__(self, config, base_folder):
        super(ModelSet, self).__init__(config, base_folder)

    def reload(self):

        model_folder = self.artifacts["model"]["local_absolute"]

        logger.info("Reload models")
        self.model = joblib.load(
            os.path.join(
                self.base_folder,
                model_folder,
                self.artifacts["model"]["name"],
            )
        )

    def predict(self, data):

        return self.model.predict(data)


@click.command()
@click.option(
    "-c",
    "--config",
    type=str,
    default=os.getenv("CONFIG_FILE"),
    help="Path to config file",
)
def predict(config):

    base_folder = os.getenv("BASE_FOLDER")
    logger.debug(f"base folder is: {base_folder}")
    logger.debug(f"config: {config}")

    _CONFIG = Config(config, base_folder=base_folder)
    preprocessed_data_config = _CONFIG[["preprocessing", "dataset", "preprocessed"]]
    rf_config = _CONFIG[["model", "rf"]]

    # create folders
    prepare_folders(_CONFIG[["model", "rf", "artifacts", "model", "local"]], base_folder=base_folder)

    # load some data
    dataset_folder = _CONFIG[["model", "rf", "artifacts", "dataset", "local_absolute"]]
    df = pd.read_parquet(
        os.path.join(dataset_folder, "model_X_test.parquet")
    ).sample(1)

    # model
    logger.debug(f"Prepare modelset and dataset")
    M = ModelSet(config=rf_config, base_folder=base_folder)
    M.reload()
    logger.info(
        M.predict(df)
    )


if __name__ == "__main__":
    predict()
```