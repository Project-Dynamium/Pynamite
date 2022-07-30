import json,os,sys
import motor.motor_asyncio as mongo

import pydantic
from bson.objectid import ObjectId
pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str

os.chdir(sys.path[0])

with open("../config.json") as f:
    conf = json.load(f)

mongo_cli = mongo.AsyncIOMotorClient(conf["mongodb_address"])
db = mongo_cli[conf["mongodb_dbname"]]
