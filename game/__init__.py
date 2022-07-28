import json,os,sys
import motor.motor_asyncio as mongo

os.chdir(sys.path[0])

with open("../config.json") as f:
    conf = json.load(f)

mongo_cli = mongo.AsyncIOMotorClient(conf["mongodb_address"])
db = mongo_cli[conf["mongodb_dbname"]]

def graphql_like_error(err):
    graphql_err = {
	"errors":[{
            "message": "Unknown Error",
            "locations": [{
                "line": 0,
                "column": 0
            }],
		"path": ["What do you looking for?"]
	    }]
    }
    graphql_err["errors"][0]["message"]=err
    return graphql_err

error_dic = {
    "not_from_game_connection":"别爬我服务器了 让我省点钱罢",
    "login_error":" 无效的用户名或密码。\nError: Invalid username or password.",
    "invalid_token":"登录已过期或无效，请重新登录。\nError: Your login session has expired or is invalid. Please re-login."
}
