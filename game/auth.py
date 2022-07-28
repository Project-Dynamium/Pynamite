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

    def user_token_checker(self, token, _id = ""):
        def _check(token, _id = ""):
            if _id != "" :
                if _id not in self.user_token.keys():
                    return False
                if token != self.user_token[_id]:
                    del self.user_token[_id]
                    return False
                return True
            else:
                for x_soudayo in self.user_token:
                    if token == x_soudayo:
                        return True
            return False
        if not _check(token, _id):
            raise Exception(error_dic["invalid_token"])

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
