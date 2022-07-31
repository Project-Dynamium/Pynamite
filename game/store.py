from __init__ import *

# Public

# Private
async def get_local_set(_id):
    doc = await db["User"].find_one({"_id":ObjectId(_id)})
    if doc == None:
        return None
    else:
        return doc["local_chart"]