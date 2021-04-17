from loguru import logger


class ModelSet:
    """
    `ModelSet` is the core of the model including hyperparameters.

    !!! warning
        This class is a proposed framework. There are many member functions to be implemented if you are using the `ModelSet` class.

        In most projects, we do not need to use this class. We have a class `ModelSetX` which is a more detailed implementation in our `model.pipeline` module.

    """

    def __init__(self, config, base_folder):
        self.config = config
        self.base_folder = base_folder

        logger.debug(
            f"base folder: {self.base_folder}\n" f"artifacts configs: {self.artifacts}"
        )

    def create_model(self):
        """
        `create_model` creates the model and updates the property `self.model`.
        """
        ...

    @property
    def hyperparameters(self):
        """
        `hyperparameters` specifies the hyperparameters. This is a property.
        """
        ...
