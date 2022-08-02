from atexit import register
from __init__ import *

# Public
async def get_store_set(skip,limit,ranked=False,unranked=False,rev_date=False,search=""):
    # Avoid reserved character conflicts
    for i in range(0,32):
        reserved = r'~!@#$%^&*()_+{}|:"<M>?`-=[]\;,./'
        search = search.replace(reserved[i]," ")

    q = [
        {"$skip":skip},
        {"$limit":limit},
    ]
    if ranked:
        q.insert(0,{"$match":{"isRanked":True}})
    if unranked:
        q.insert(0,{"$match":{"isRanked":False}})
    if search != "":
        reg = {"$regex": search, "$options": "i"}
        reg = {"$match":
                {"$or": [
                    {"musicTitle": reg },
                    {"noter": {"username":reg}},
                    {"composerName":reg},
            ]}
        }
        q.insert(0,reg)
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
    return doc["set_id"] if doc != None else None


# Private
async def get_local_set(_id):
    doc = await db["User"].find_one({"_id":ObjectId(_id)})
    if doc == None:
        return None
    else:
        return doc["local_chart"]