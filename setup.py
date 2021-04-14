from setuptools import find_packages as _find_packages
from setuptools import setup as _setup

from haferml.version import __version__

PACKAGE_NAME = "hafer"
PACKAGE_VERSION = __version__
PACKAGE_DESCRIPTION = "HAFER ML, the homemade framework for machine learning"
PACKAGE_LONG_DESCRIPTION = (
    "HAFER ML, the homemade framework for machine learning, is a simple and unambitious framework for small machine learning projects, with reproducibility in mind."
)
PACKAGE_URL = "https://github.com/emptymalei/haferml"


def _requirements():
    return [r for r in open("requirements.txt")]


def get_extra_requires(path, add_all=True):
    """
    get_extra_requires retrieves the extras requirements.

    Reference:
    https://hanxiao.io/2019/11/07/A-Better-Practice-for-Managing-extras-require-Dependencies-in-Python/

    :param path: path to the extras require specification
    :type path: str
    :param add_all: whether to include the keyword all, defaults to True
    :type add_all: bool, optional
    :return: The mapping of all the dependencies by extras keyword
    :rtype: dict
    """
    import re
    from collections import defaultdict

    with open(path) as fp:
        extra_deps = defaultdict(set)
        for k in fp:
            if k.strip() and not k.startswith("#"):
                tags = set()
                if ":" in k:
                    k, v = k.split(":")
                    tags.update(vv.strip() for vv in v.split(","))
                tags.add(re.split("[<=>]", k)[0])
                for t in tags:
                    extra_deps[t].add(k)

        # add tag `all` at the end
        if add_all:
            extra_deps["all"] = set(vv for v in extra_deps.values() for vv in v)

    return extra_deps


def setup():
    _setup(
        name=PACKAGE_NAME,
        version=PACKAGE_VERSION,
        description=PACKAGE_DESCRIPTION,
        long_description=PACKAGE_LONG_DESCRIPTION,
        url=PACKAGE_URL,
        author="Lei Ma",
        author_email="hi@leima.is",
        license="MIT",
        packages=_find_packages(exclude=("tests",)),
        install_requires=_requirements(),
        include_package_data=True,
        test_suite="nose.collector",
        tests_require=["nose"],
        extras_require=get_extra_requires("requirements.extras.txt"),
        zip_safe=False,
    )


if __name__ == "__main__":
    setup()
    print(_find_packages(exclude=("tests",)))
