from __init__ import *
from copy import deepcopy
import math

import store, time

# Read
async def get_chart_ranking(chartId, skip, limit):
    doc = (await db["Chart"].find_one({"_id":ObjectId(chartId)}))["ranking"]
    if skip > len(doc):
        return []
    if skip + limit > len(doc):
        return doc[skip:]
    return doc[skip:skip+limit]

def calc_R(perfect,great,miss,rValue):
    if perfect == 0 or math.ceil(rValue) == 0:
        return 0
    # R algorithm by @Crazy_bull(https://space.bilibili.com/335803482)
    x = rValue
    y = (perfect*2+great)/float((perfect + great + miss)*2)

    p = [279.8797946871640,528.3010777498843,422.1282045808567,138.5807381040514,318.2521180218479,-21.36049015563466,89.79916598438198,
    256.7692542088084,110.0442908135585,25.68573628812841,-3.455751278271652,-11.24395409094263,-46.03561353299639,-42.40553252921365,
    -12.24599454333353,8.917718764126615,33.54545384331117,33.21600510917200,29.97371473065533,21.75010922773462,4.694350847362575,
    -2.073168425985943,-8.527466920637410,-11.41739617279520,-13.75800798367046,-14.30516423357537,-8.346583655814630,-0.8935352407485705,
    0.7149903885144406,3.578455242068043,3.792436829426481,4.081955340549154,6.230838409222139,5.493788245974849,1.699357971629093,
    -0.07954682336265180,-0.09289519073554239,-0.8852091399790804,-0.9656173948291340,-0.6199915055987623,-1.480634925070910,
    -2.211984841680285,-1.159184044952558,0.06908243025789186,0.07864886989688262,0.005595506761079347,0.1204755520362488,0.1940419763008610,
    0.02524697925679845,0.1287906618910464,0.4217782149408803,0.3857828065570721,0.07513286986808960,-0.08026294653892107,-0.01314000678177232,]

    order = 54
    logx = 1
    logy =1

    s = [11.35000000000000, 5.650000000000000,
    2.286839759448360, 0.5463735846078558,
    0.9677015525000000, 0.03229844749999999,
    -0.03338885713016246, 0.03338885713016246]

    ans = 0.0

    x = (x - s[0]) / s[1] if logx == 0 else (math.log(x) - s[2]) / s[3]
    y = (y - s[4]) / s[5] if logy == 0 else (math.log(y) - s[6]) / s[7]
            
    tcnt = 10

    if x < -1.0 :
        x = -1.0
    if x > 1.0 :
        x = 1.0
    if y < -1.0 :
        y = -1.0
    if y > 1.0 :
        y = 1.0

    tx = [1.0,x,0,0,0,0,0,0,0,0]
    ty = [1.0,y,0,0,0,0,0,0,0,0]
    v = [0.0 for i in range(0,70)]

    for j in range(2,tcnt):
        tx[j] = 2 * x * tx[j - 1] - tx[j - 2]
        ty[j] = 2 * y * ty[j - 1] - ty[j - 2]

    iv = 0
    for j in range(0,tcnt):
        m = j
        while m>=0:
            v[iv] = tx[m] * ty[j - m]
            iv+=1
            m-=1
    ans = 0.0
    for j in range(0,order+1):
        ans += p[j] * v[j]
    
    return round(ans) if ans > 0 else 0

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
            break
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