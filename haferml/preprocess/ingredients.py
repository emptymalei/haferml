import inspect
import time
from functools import wraps

from loguru import logger


def attributes(**attrs):
    """
    A decorator to set attributes of member functions in a class.

    ```python
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


def order(ord):
    """
    `order` is decorator to order the pipeline classes. This decorator specifies a property named "order" to the member function so that we can use the property to order the member functions.

    This `order` function can be combined with the decorator `with_transforms` which orders the member functions.

    ```python
    class AGoodClass:
        def __init__(self):
            self.size = 0

        @order(1)
        def first_good_member(self, new):
            return "first good member"

        @order(2)
        def second_good_member(self, new):
            return "second good member"
    ```
    """
    return attributes(order=ord)


def with_transforms(attr=None):
    """
    with_transforms is a decorator that builds the ordered transformations and
    assigns the transforms to the property `self.transforms`. `self.transforms`
    is a dictionary and the keys are the name of the transformation functions.


    ```python
    @with_transforms
    def run(self):
        for t in self.transforms:
            dataframe = self.transforms[t](dataframe)
            logger.info(f"transformation {t} is done.")
    ```

    Here is a full example of the decorator.

    ```python
    class AGoodClass:
        def __init__(self):
            pass

        @order(1)
        def first_good_member(self, new):
            return f"{new} - appended first good member"

        @order(2)
        def second_good_member(self, new):
            return f"{new} - appended second good member"

        @with_transforms()
        def bench(self, name):
            logger.info(name)
            logger.info(self.transforms)
            for t in self.transforms:
                name = self.transforms[t](name)
                logger.info(f"transformation {t} is done. Got strings: {name}")

    a = AGoodClass()

    a.bench("a name")
    ```

    If you would rather use a different attribute name such as "rank", the `with_transforms` decorator can also be customized.

    ```python
    class AGoodClass:
        def __init__(self):
            pass

        @attributes(rank=1)
        def first_good_member(self, new):
            return f"{new} - appended first good member"

        @attributes(rank=2)
        def second_good_member(self, new):
            return f"{new} - appended second good member"

        @with_transforms(attr="rank")
        def bench(self, name):
            logger.info(name)
            logger.info(self.transforms)
            for t in self.transforms:
                name = self.transforms[t](name)
                logger.info(f"transformation {t} is done. Got strings: {name}")

    a = AGoodClass()

    a.bench("a name")
    ```

    """
    if attr is None:
        attr = "order"

    def _with_transforms(f):
        def _get_transforms(self, *args):
            all_methods = dict(inspect.getmembers(self))
            transforms = []

            for method_name, method_func in all_methods.items():
                if hasattr(method_func, attr):
                    method_order = getattr(method_func, attr)
                    logger.debug(f"{method_name} has order {method_order}")

                    transforms.append(
                        {"name": method_name, "method": method_func, attr: method_order}
                    )
            transforms = sorted(transforms, key=lambda k: k[attr])
            self.transforms = {m["name"]: m["method"] for m in transforms}

            logger.debug("All methods: {}".format(all_methods))
            logger.debug("Ordered predefined transformers: {}".format(self.transforms))

            return f(self, *args)

        return _get_transforms

    return _with_transforms


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
        _get_transforms extracts the list of transformers.

        This method can be replaced by the decorator `with_transforms`.
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
