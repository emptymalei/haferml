from loguru import logger


class ModelWorkflow:
    """ModelWorkflow class that holds DataSet and ModelSet.

    !!! warning
        This class is a proposed framework. There are many member functions to be implemented if you are using the `ModelWorkflow` class.

        In most projects, we do not need to use this class. We have a class `ModelWorkflowX` which is a more detailed implementation in our `model.pipeline` module.

    `ModelWorkflow` takes a few arguments to instantiate. To run the workflow, use the `train` method.

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

    def fit_and_report(self):
        """
        `_fit_and_report` fits the model using input data and generate reports.

        !!! warning
            Please implement this method.
        """
        ...

    def export_results(self):
        """
        export_results saves the necessary artifacts

        !!! warning
            Please implement this method.
        """
        ...

    def train(self, dataset):
        """
        train connects the training workflow and executes the workflow step by step.
        """

        logger.info("1. Create train test datasets")
        self.DataSet.create_train_test_datasets(dataset)
        logger.info("2. Create model")
        self.ModelSet.create_model()
        logger.info("3. Fit model and report")
        self.fit_and_report()
        logger.info("4. Export results")
        self.export_results()
