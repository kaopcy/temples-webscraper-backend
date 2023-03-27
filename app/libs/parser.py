import json

from bson.objectid import ObjectId


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)


def json_parser(data={}):
    return json.loads(json.dumps(data, cls=JSONEncoder))
