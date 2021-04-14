import datetime

import dateutil
import numpy as np
import simplejson as json

######################
#  JSON
######################


class JSONEncoder(json.JSONEncoder):
    """
    data serializer for json
    """

    def default(self, obj):
        """
        default serializer
        """
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return {"__type__": "__datetime__", "datetime": obj.isoformat()}

        return json.JSONEncoder.default(self, obj)


def decode(obj):
    """
    decode decodes the JSONEncoder results
    """
    if "__type__" in obj:
        if obj["__type__"] == "__datetime__":
            return dateutil.parser.parse(obj["datetime"])
    return obj


def isoencode(obj):
    """
    isoencode decodes many different objects such as
    np.bool -> regular bool
    """
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.int64):
        return int(obj)
    if isinstance(obj, np.float64):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


if __name__ == "__main__":

    pass
