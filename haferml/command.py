import os
import time

import click
import simplejson as json
from loguru import logger

__CWD__ = os.getcwd()


@click.group(invoke_without_command=True)
@click.pass_context
def haferml(ctx):
    if ctx.invoked_subcommand is None:
        click.echo("Hello {}".format(os.environ.get("USER", "")))
        click.echo("Welcome to HaferML. Use `haferml --help` to find all the commands.")
    else:
        click.echo("Loading Service: %s" % ctx.invoked_subcommand)


@haferml.command()
@click.argument("path", type=str, required=True)
def config(path=None):
    """Generate config file at the specified location.

    :param path: where to create the config file.
    :param path: str
    """

    click.secho(f"Creating config file at location: {path}")
    path_folder = os.path.dirname(path)

    if not os.path.exists(path_folder):
        if click.confirm(
            f"Folder {path_folder} doesn't exist. Shall we create it?", abort=True
        ):
            click.echo(f"Creating folder {path_folder} ...")
            os.makedirs(path_folder)

    config = {
        "name": "Example: A HaferML Project",
        "etl": {
            "cache_folder": "cache",
            "raw": {
                "local": "data/raw",
                "remote": "",
                "my_raw_data": {
                    "name": "my_raw_data.csv",
                    "local": "data/raw",
                    "remote": "s3://",
                },
            },
            "transformed": {
                "local": "dataset/etl",
                "remote": "",
                "my_raw_data": {
                    "name": "my_data.parquet",
                    "local": "dataset/etl",
                    "remote": "s3://",
                },
            },
        },
        "preprocessing": {
            "dataset": {
                "local": "model/dataset",
                "remote": "",
                "preprocessed": {
                    "name": "preprocessed.parquet",
                    "local": "model/dataset",
                    "remote": "s3://",
                },
            },
            "features": [],
            "targets": [],
            "feature_engineering": {},
            "target_engineering": {},
        },
        "model": {
            "rf": {
                "features": [],
                "targets": [],
                "encoding": {"categorical_columns": []},
                "random_state": 42,
                "test_size": 0.3,
                "cv": {"folds": 5, "n_iter": 10},
                "hyperparameters": {},
                "artifacts": {
                    "dataset": {"local": "model/dataset", "remote": "s3://"},
                    "model": {
                        "name": "model.joblib",
                        "local": "model/model",
                        "remote": "s3://",
                    },
                    "prediction": {"local": "prediction", "remote": "s3://"},
                    "performance": {"local": "performance", "remote": "s3://"},
                },
            }
        },
    }

    if os.path.isfile(path):
        if click.confirm(f"Config file {path} already exists. Override?", abort=True):
            click.echo(f"Will override {path}; Waiting for 5 seconds ...")
            with click.progressbar(range(5, -1, -1)) as bar:
                for i in bar:
                    time.sleep(1)
            with open(path, "w") as fp:
                json.dump(config, fp, indent=2)
    else:
        click.echo(f"Creating {path} ...")
        with open(path, "x") as fp:
            json.dump(config, fp, indent=2)


if __name__ == "__main__":

    pass
