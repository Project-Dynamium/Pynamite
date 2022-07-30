from __init__ import *

# Read
async def get_user_info(_id):
    doc = await db["User"].find_one({"_id":ObjectId(_id)})
    return doc

# Write
async def update_info(info, _id):
    doc = await db["User"].find_one({"_id":ObjectId(_id)})
    for key in info.keys():

        if key == "username":
            return
        elif key == "password":
            return

        else:
            doc[key] = info[key]
    
    db["User"].update_one({"_id":ObjectId(_id)}, {"$set":doc})