from __init__ import *

import time, hashlib

class token_maintainer:
    user_token = {}
    score_token = {}

    def token_generator(self, input):
        return hashlib.md5((str(time.time())+input).encode()).hexdigest()

    def store_user_token(self, username, _id, token):
        # Token from client is named as x-soudayo
        self.user_token[_id] = {
            "username":username,
            "token":token,
            "enlist_time":int(time.time())
        }

    def user_token_checker(self, token, _id = None, return_id = False):
        def _check(token, _id):
            if _id != None :
                if _id not in self.user_token.keys():
                    return False
                if token != self.user_token[_id]["token"]:
                    del self.user_token[_id]
                    return False
                return True
            else:
                for id, context in self.user_token.items():
                    if context["token"] == token:
                            return (id if return_id else True)
            return False
        result = _check(token, _id)
        if result == False:
            raise Exception(error_dic["invalid_token"])
        return result

    def store_score_token(self, uid, s_token, sid):
        self.score_token[uid] = {
            "uid":uid,
            "token":s_token,
            "sid":sid,
            "enlist_time":int(time.time())
        }

    def store_score_token(self, uid, s_token, sid):
        self.score_token[uid] = {
            "uid":uid,
            "token":s_token,
            "sid":sid,
            "enlist_time":int(time.time())
        }

    def score_token_checker(self, uid, s_token):
        def _check(u, s):
            if self.score_token[uid]["token"] == s_token:
                return self.score_token[uid]["sid"]
            else:
                return False
        result = _check(uid, s_token)
        if result == False:
            raise Exception(error_dic["invalid_token"])
        return result
             
security_manager = token_maintainer()

async def login(username, password, user):
    # Fetch userinfo
    sha256_pwd = hashlib.sha256(password.encode()).hexdigest()
    doc = await db["User"].find_one({
        "username":username,
        "password":sha256_pwd
    })
    if doc == None:
        raise Exception(error_dic["login_error"])

    user._id=doc["_id"].__str__()
    user.username=doc["username"]
    user.token = security_manager.token_generator(user._id)
    user.coin=doc["coin"]
    user.diamond=doc["diamond"]
    #user.PPTime=doc["PPTime"]
    user.RThisMonth=doc["RThisMonth"]
    #user.access=doc["access"]

    security_manager.store_user_token(user.username,user._id,user.token)
    return user  
