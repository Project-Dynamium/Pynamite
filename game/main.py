from wsgiref.util import request_uri
from fastapi import FastAPI, Request, Response
import uvicorn

from __init__ import *
from graphQL.handle import *

if conf["debug"]:
    app = FastAPI()
else:
    app = FastAPI(docs_url=None, redoc_url=None)

@app.post(conf["url_prefix"]+"/graphql")
async def handle(request: Request):
    data = await request.json()
    print(data) # DEBUG
    #if request.headers.get("user-agent") != "dynamite/59 CFNetwork/1333.0.4 Darwin/21.5.0":
    #   return graphql_like_error(error_dic["not_from_game_connection"])
    
    schema = strawberry.Schema(query = Query, mutation = Mutation, config = StrawberryConfig(auto_camel_case = False))
    if "variables" not in data.keys():
        graphql_ret = await schema.execute(data['query'], context_value=request.headers.get("x-soudayo"))
    else:
        graphql_ret = await schema.execute(data['query'], data['variables'], request.headers.get("x-soudayo"))
    print(graphql_ret)  # DEBUG

    if graphql_ret.errors != None:
        err_msg = ""
        for err in graphql_ret.errors:
            err_msg += err.message + " "
        return graphql_like_error(err_msg)

    print("\n\n",graphql_ret.__dict__)
    return graphql_ret.__dict__

from auth import security_manager
@app.post("/internal/check_login")
async def handle(request: Request):
    try:
        if request.client.host != "127.0.0.1":
            return Response(status_code=403)
        data = await request.json()
        user_id = security_manager.user_token_checker(data["token"],return_id=True)
        return {"status":200,"_id":user_id}
    except Exception as e:
        return {"status":403}


if __name__ == "__main__":
    os.chdir(sys.path[0])
    if conf["https"]:
        uvicorn.run("main:app",
            host = "0.0.0.0", 
            port = conf["game_port"], 
            reload = conf["server_hot_reload"],
            ssl_keyfile = conf["https_key"], 
            ssl_certfile = conf["https_cert"]
        )
    else:
        uvicorn.run("main:app",
            host = "0.0.0.0", 
            port = conf["game_port"], 
            reload = conf["server_hot_reload"]
        )