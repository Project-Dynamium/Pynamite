from __init__ import *
from copy import deepcopy
from decimal import Decimal

import store, time

# Read
def calc_R(p,g,m,v):
    p = Decimal(p)
    g = Decimal(g)
    m = Decimal(m)
    s = Decimal(v)
    a = p+g+m

    maxr = Decimal("70")/Decimal("3")*s*s - Decimal("1175")/Decimal("3")*s + Decimal(2035.6)
    gs=s*maxr/Decimal(2)/a+Decimal(2)-maxr/a
    ms=s*maxr/a+Decimal(2)-maxr/a
    gz=s*maxr/Decimal(2)/a+Decimal(2)-(gs/a*g+gs/a*g)
    mz=s*maxr/a+Decimal(2)-ms/a*m
    rresult = maxr - g*gz-m*mz
    return int(rresult.quantize(Decimal('0')))

# Write
async def update_ranking_list(uid, cid, profile):
    doc = (await db["Chart"].find_one({"_id":ObjectId(cid)}))["ranking"]
    s = deepcopy(profile)
    del s["chart_id"]
    s["uid"] = uid

    for i in range(0,len(doc)):
        if doc[i]["uid"] == uid:
            if doc[i]["s"] < doc[i]["s"]: 
                doc[i] = s
                doc.sort(key = lambda x:x["s"],reverse=True)
                await db["Chart"].update_one({"_id":ObjectId(cid)},{"$set":{"ranking":doc}})    
            break
    else:
        doc.append(s)
        doc.sort(key = lambda x:x["s"],reverse=True)
        await db["Chart"].update_one({"_id":ObjectId(cid)},{"$set":{"ranking":doc}}) 
        

async def update_rank_score(uid, cid, v, doc, r):
    new_score = {
        "chart_id": cid,
        "create_time": time.time(),
        "s":r.score,
        "p":r.perfect,
        "g":r.good,
        "m":r.miss,
        "R":calc_R(r.perfect,r.good,r.miss,v)
    }

    for i in range(0,len(doc["rank_score"])):
        if doc["rank_score"][i]["chart_id"] == cid:
            if doc["rank_score"][i]["s"] < new_score["s"]: 
                doc["rank_score"][i] = new_score
                await update_ranking_list(uid, cid, new_score)
            break
    else:
        doc["rank_score"].append(new_score)
        await update_ranking_list(uid, cid, new_score)

    for i in range(0,len(doc["best_R"])):
        if doc["best_R"][i]["chart_id"] == cid:
            if doc["best_R"][i]["R"] < new_score["R"]: 
                doc["best_R"][i] = new_score
                doc["best_R"].sort(key = lambda x:x["R"],reverse=True)
    else:
        doc["best_R"].append(new_score)
        doc["best_R"].sort(key = lambda x:x["R"],reverse=True)
    
    total_R = 0
    for i in range(0, 20 if len(doc["best_R"])>20 else len(doc["best_R"])):
        total_R += doc["best_R"][i]["R"]
    
    doc["RThisMonth"] = total_R
    return doc

async def update_unrank_score(uid, cid, doc, r):
    new_score = {
        "chart_id": cid,
        "create_time": time.time(),
        "s":r.score,
        "p":r.perfect,
        "g":r.good,
        "m":r.miss
    }

    print(doc)
    for i in range(0,len(doc["unrank_score"])):
        if doc["unrank_score"][i]["chart_id"] == cid:
            if doc["unrank_score"][i]["s"] < new_score["s"]: 
                doc["unrank_score"][i] = new_score
                await update_ranking_list(uid, cid, new_score)
            break
    else:
        doc["unrank_score"].append(new_score)
        await update_ranking_list(uid, cid, new_score)

    return doc

async def update_score(uid, cid, playRecord, AfterRecord):
    profile = (await db["User"].find_one({"_id":ObjectId(uid)}))
    sid = await store.get_chart_set(cid)
    chart = await db["Set"].find_one({"_id":ObjectId(sid)})

    if chart == None:
        raise Exception("Invalid Chart.")

    if chart["isRanked"]:
        rV = (await db["Chart"].find_one({"_id":ObjectId(cid)}))["rValue"]
        r = await update_rank_score(uid, cid, rV, profile, playRecord)
    else:
        r = await update_unrank_score(uid, cid, profile, playRecord)

    await db["User"].update_one({"_id":ObjectId(uid)},{"$set":r})    

    ranking = (await db["Chart"].find_one({"_id":ObjectId(cid)}))["ranking"]
    for i in range(0,len(ranking)):
        if ranking[i]["uid"] == uid:
            AfterRecord.ranking.playRank.rank = i+1
            break
    else:
        AfterRecord.ranking.playRank.rank = -1
    
    AfterRecord.coin = r["coin"]
    AfterRecord.RThisMonth = r["RThisMonth"]
    AfterRecord.diamond = r["diamond"]
    AfterRecord.ranking.isPlayRankUpdated = True
    return AfterRecord