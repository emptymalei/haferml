from nose import tools as _tools
from haferml.blend.config import Config


def test_Config_with_base_folder():

    test_config = {
        "etl": {
            "raw": {
                "transactions": {
                    "local": "abc",
                    "name": "def.parquet",
                    "remote": ""
                },
                "model": {
                        "local": "abc",
                        "remote": ""
                    },
            }
        },
        "model": {
            "rf": {
                "artifacts": {
                    "model": {
                        "local": "abc",
                        "remote": ""
                    },
                    "prediction": {
                        "local": "abc",
                        "remote": ""
                    }
                }
            }
        }
    }

    conf = Config(test_config, base_folder="/tmp")

    _tools.eq_(conf.get(["etl", "raw", "model", "local"]), "abc")
    _tools.eq_(conf.get(["etl", "raw", "model"]), {"local": "abc", "local_absolute": "/tmp/abc", "remote": ""})

    _tools.eq_(
        conf.get(["etl", "raw", "transactions"]),
        {
            "local": "abc",
            "local_absolute": "/tmp/abc",
            "name": "def.parquet",
            "name_absolute": "/tmp/abc/def.parquet",
            "remote": ""
        }
    )


def test_Config_without_base_folder():

    test_config = {
        "etl": {
            "raw": {
                "transactions": {
                    "local": "abc",
                    "name": "def.parquet",
                    "remote": ""
                },
                "model": {
                        "local": "abc",
                        "remote": ""
                    },
            }
        },
        "model": {
            "rf": {
                "artifacts": {
                    "model": {
                        "local": "abc",
                        "remote": ""
                    },
                    "prediction": {
                        "local": "abc",
                        "remote": ""
                    }
                }
            }
        }
    }

    conf = Config(test_config)

    _tools.eq_(conf.get(["etl", "raw", "model", "local"]), "abc")
    _tools.eq_(conf.get(["etl", "raw", "model"]), {"local": "abc", "local_absolute": "abc", "remote": ""})


    _tools.eq_(
        conf.get(["etl", "raw", "transactions", "name_absolute"]),
        "abc/def.parquet"
    )

    _tools.eq_(
        conf.get(["etl", "raw", "transactions"]),
        {
            "local": "abc",
            "local_absolute": "abc",
            "name": "def.parquet",
            "name_absolute": "abc/def.parquet",
            "remote": ""
        }
    )
