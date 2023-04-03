from datetime import date, datetime

import isodate as iso
from bson import ObjectId
from flask import abort
from flask.json import JSONEncoder
from werkzeug.routing import BaseConverter


class MongoJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime, date)):
            return iso.datetime_isoformat(o)
        if isinstance(o, ObjectId):
            return str(o)
        else:
            return super().default(o)


class ObjectIdConverter(BaseConverter):
    def to_python(self, value):
        return ObjectId(value)

    def to_url(self, value):
        return str(value)

def find_restaurants(mongo, _id=None):
    if _id:
        try:
            result = mongo.db.restaurant.find_one({"_id": ObjectId(_id)})
        except Exception as e:
            return (f"No restaurant found with the ID: {_id}", 204)
    else:
        result = list(mongo.db.restaurant.find())
    return result