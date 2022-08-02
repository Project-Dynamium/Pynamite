from __init__ import *

# Public
async def get_store_set(skip,limit,ranked=False,unranked=False,rev_date=False):
    q = [
        {"$skip":skip},
        {"$limit":limit},
    ]
    if ranked:
        q.insert(0,{"$match":{"isRanked":True}})
    if unranked:
        q.insert(0,{"$match":{"isRanked":True}})
    if not rev_date:
        q.insert(0,{"$sort":{"_id":-1}})

    doc = []
    async for r in db["Set"].aggregate(q):
        doc.append(r)
    return doc if doc != None else []

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