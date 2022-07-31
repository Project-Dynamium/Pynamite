from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, Response
import uvicorn
import httpx

from __init__ import *

if conf["debug"]:
    app = FastAPI()
else:
    app = FastAPI(docs_url=None, redoc_url=None)

import user.auth as auth
import user.profile as profile

# For game resource distribution
# Public distribute
@app.get("/download/cover/480x270_jpg/{_id}")
async def handle():
    return RedirectResponse("http://192.168.5.4:5666/test123",status_code=302)

@app.get("/download/avatar/256x256_jpg/{_id}")
async def handle():
    return RedirectResponse("http://192.168.5.4:5666/test123",status_code=302)

@app.get("/download/music/encoded/")
async def handle(request: Request):
    return

# Local distribute
    
@app.get("/download/{info:path}")
async def local_cover_distribute(request: Request, info: str):
    result = httpx.post("http://127.0.0.1:{}/internal/check_login".format(str(conf["game_port"])),
        json={"token":request.headers.get("x-soudayo")}).json()
    if result["status"] == 403:
        return Response(content="Invalid token.", status_code=403)

    info = info.split("/")
    if info[-1][2:7] == "local" and info[-1][0] == "0":
        #del info[-2]
        local_ip = (await profile.get_user_info(result["_id"]))["local_ip"]
        return RedirectResponse("http://{}:10442/{}".format(local_ip,"/".join(info)),status_code=302)


    return Response(status_code=404)

# For game data management
# User
@app.post("/manage/login")
async def external_login(request: Request):
    try:
        data = await request.json()
        print(data) # DEBUG

        result = await auth.login(data["username"],data["password"],data["sha256"])
        return result
        
    except Exception as e:
        if str(e) == "login_err":
            return Response(content="Invalid username or password.", status_code=403)
        print(e) # DEBUG
        return Response(status_code=500)

@app.post("/manage/user/update")
async def update_profile(request: Request):
    try:
        data = await request.json()
        _id = data["_id"]
        print(data) # DEBUG
        auth.security_manager.user_token_checker(request.headers.get("token"),_id)

        for key in data["update"].keys():
            if key not in ["username","password","local_ip","local_chart"]:
                return Response(content="Invalid request.", status_code=403)
        
        await profile.update_info(data["update"],_id)
        
        return await profile.get_user_info(_id)
        
    except Exception as e:
        if str(e) == "Invalid token":
            return Response(content="Invalid token.", status_code=403)
        if str(e) == "Duplicated username.":
            return Response(content="Duplicated username.", status_code=403)
        print(e) # DEBUG
        return Response(status_code=500)

if __name__ == "__main__":
    os.chdir(sys.path[0])
    if conf["https"]:
        uvicorn.run("main:app",
            host = "0.0.0.0", 
            port = conf["api_port"], 
            reload = conf["server_hot_reload"],
            ssl_keyfile = conf["https_key"], 
            ssl_certfile = conf["https_cert"]
        )
    else:
        uvicorn.run("main:app",
            host = "0.0.0.0", 
            port = conf["api_port"], 
            reload = conf["server_hot_reload"]
        )
