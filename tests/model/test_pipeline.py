from nose import tools as _tools
from haferml.model.pipeline import *

conf = {
    "artifacts": {
        "model": {"local": "abc", "remote": ""},
        "prediction": {"local": "abc", "remote": ""},
    }
}

test_dsx = DataSetX(conf, "/tmp")
