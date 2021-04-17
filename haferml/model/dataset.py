from loguru import logger


class DataSet:
    """
    DataSet to be used in a model workflow.

    !!! warning
        This class is a proposed framework. There are many member functions to be implemented if you are using the `DataSet` class.

        In most projects, we do not need to use this class. We have a class `DataSetX` which is a more detailed implementation in our `model.pipeline` module.


    The interface of this class in a workflow is the `create_train_test_datasets` method.

    Depending on the requirements, one can also implement a method `_export_train_test_data` to save the dataset locally or remotely.

    """

    def __init__(self, config, base_folder):
        self.config = config
        self.base_folder = base_folder

    def create_train_test_datasets(self):
        """
        create_train_test_datasets is our interface to our workflow.

        !!! warning
            Please implement this method.

        One could call the `_export_train_test_data` method to export the dataset locally or remotely.
        """
        ...

    @staticmethod
    def _save_data(dataframe, destination):
        """
        `_save_data` is dummy method method to save the data to a local destination.

        !!! warning
            Please implement this method.

        :param dataframe: a pandas dataframe that holds the data
        :type dataframe: pandas.DataFrame
        :param destination: destination of the data on a local machine
        :type destination: str
        """
        logger.debug(f"Saving data to {destination} ...")
        dataframe.to_parquet(destination)

    def _export_train_test_data(self):
        """
        _export_train_test_data saves train and test datasets.

        !!! warning
            Please implement this method.

        """
        ...
