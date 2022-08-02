from __init__ import *

# Public
async def get_set_chart(_id):
    doc = await db["Set"].find_one({"_id":ObjectId(_id)})
    return doc if doc != None else []

async def get_chart_set(_id):
    doc = await db["Chart"].find_one({"_id":ObjectId(_id)})
    return doc["set_id"] if doc != None else 404


# Private
async def get_local_set(_id):
    doc = await db["User"].find_one({"_id":ObjectId(_id)})
    if doc == None:
        return None
    else:
        return doc["local_chart"]