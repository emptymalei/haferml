# Rideindego Config

We use one single global config for the whole project. It is highly recommended to place the config json file inside the artifacts folder so that we can restore everything later when syncing the whole artifacts folder.

```json
{
    "name": "rideindego prices",
    "etl": {
        "cache_folder": "cache",
        "raw": {
            "local": "data/raw",
            "remote": "s3://haferml-rideindego/marshall/data/raw",
            "stations": {
                "name": "stations.parquet",
                "local": "data/raw/stations",
                "remote": "s3://haferml-rideindego/marshall/data/raw/stations"
            },
            "trip_data": {
                "source": "https://www.rideindego.com/about/data/",
                "name": "trips.parquet",
                "local": "data/raw/trip_data",
                "remote": "s3://haferml-rideindego/marshall/data/raw/trip_data"
            }
        },
        "transformed": {
            "local": "dataset/etl",
            "remote": "s3://haferml-rideindego/marshall/dataset/etl",
            "stations": {
                "name": "stations.parquet",
                "local": "dataset/etl",
                "remote": "s3://haferml-rideindego/marshall/dataset/etl"
            },
            "trip_data": {
                "name": "trips.parquet",
                "local": "dataset/etl",
                "remote": "s3://haferml-rideindego/marshall/dataset/etl"
            }
        }
    },
    "preprocessing": {
        "dataset": {
            "local": "model/dataset",
            "remote": "s3://haferml-rideindego/marshall/model/dataset",
            "preprocessed": {
                "name": "preprocessed.parquet",
                "local": "model/dataset",
                "remote": "s3://haferml-rideindego/marshall/model/dataset"
            }
        },
        "features": [
            "passholder_type",
            "bike_type",
            "trip_route_category",
            "hour",
            "weekday",
            "month"
        ],
        "targets": [
            "duration"
        ],
        "feature_engineering": {
        },
        "target_engineering": {
        }
    },
    "model": {
        "rf": {
            "features": [
                "passholder_type",
                "bike_type",
                "trip_route_category",
                "hour",
                "weekday",
                "month"
            ],
            "targets": [
                "duration"
            ],
            "encoding": {
                "categorical_columns": [
                    "passholder_type",
                    "bike_type",
                    "trip_route_category"
                ]
            },
            "random_state": 42,
            "test_size": 0.3,
            "cv": {
                "folds": 3,
                "verbose": 6,
                "n_jobs": 1,
                "n_iter": 5
            },
            "hyperparameters": {},
            "artifacts": {
                "dataset": {
                    "local": "model/dataset",
                    "remote": "s3://haferml-rideindego/marshall/model/dataset"
                },
                "model": {
                    "name": "model.joblib",
                    "local": "model/model",
                    "remote": "s3://haferml-rideindego/marshall/model/model"
                },
                "prediction": {
                    "local": "prediction",
                    "remote": "s3://haferml-rideindego/marshall/prediction"
                },
                "performance": {
                    "local": "performance",
                    "remote": "s3://haferml-rideindego/marshall/performance"
                }
            }
        }
    }
}
```