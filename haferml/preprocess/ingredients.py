import inspect
import time
from functools import wraps

from loguru import logger


def attributes(**attrs):
    """
    A decorator to set attributes of member functions in a class.

    ```
    class AGoodClass:
        def __init__(self):
            self.size = 0

        @attributes(order=1)
        def first_good_member(self, new):
            return "first good member"

        @attributes(order=2)
        def second_good_member(self, new):
            return "second good member"
    ```

    References:
    1. https://stackoverflow.com/a/48146924/1477359

    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        for attr_name, attr_value in attrs.items():
            setattr(wrapper, attr_name, attr_value)

        return wrapper

    return decorator


class OrderedProcessor:
    """
    Go through an ordered methods in OrderedProcessor to transform a dataframe.

    Beware of the exceptions.

    Add member functions to transform the dataframe

    ```
    @attribute(order=1)
    def _transformer_created_at(self, dataframe):
        pass
    ```
    """

    def __init__(self, **params):

        self.params = params
        self._get_transforms()

        # get current timestamp
        self.current_timestamp = int(time.time())
        logger.info(f"current timestamp: {self.current_timestamp}")

    def _get_transforms(self):
        """
        _get_transforms extracts the list of transformers
        """

        all_methods = dict(inspect.getmembers(self))
        transforms = []

        for method_name, method_func in all_methods.items():
            if hasattr(method_func, "order"):
                method_order = method_func.order
                logger.info(f"{method_name} has order {method_order}")

                transforms.append(
                    {"name": method_name, "method": method_func, "order": method_order}
                )
        transforms = sorted(transforms, key=lambda k: k["order"])
        self.transforms = {m["name"]: m["method"] for m in transforms}

        logger.debug("All methods: {}".format(all_methods))
        logger.info("Ordered predefined transformers: {}".format(self.transforms))
