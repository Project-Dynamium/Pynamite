from __init__ import *

import time, hashlib, httpx

class token_maintainer:
    user_token = {}

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
            raise Exception("Invalid token")
        return result


security_manager = token_maintainer()

async def login(username, password, sha256=False):
    # Fetch userinfo
    if not sha256:
        sha256_pwd = hashlib.sha256(password.encode()).hexdigest()
    else:
        sha256_pwd = password

    doc = await db["User"].find_one({
        "username":username,
        "password":sha256_pwd
    })
    if doc == None:
        raise Exception("login_err")

    _id=doc["_id"].__str__()
    username=doc["username"]
    token = security_manager.token_generator(_id)
    coin=doc["coin"]
    diamond=doc["diamond"]
    #PPTime=doc["PPTime"]
    RThisMonth=doc["RThisMonth"]
    #access=doc["access"]

    security_manager.store_user_token(username,_id,token)
    return {
        "user":{
        "_id":_id,
        "username":username,
        "token":token,
        "coin":coin,
        "diamond":diamond,
        #PPTime=doc["PPTime"]
        "RThisMonth":RThisMonth
        #access=doc["access"]
        }
    }

async def in_game_check_login(token):
    req = httpx.post("http://127.0.0.1:10443/internal/check_login",json={"token":token}).json()
    return req
