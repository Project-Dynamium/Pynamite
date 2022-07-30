from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, Response
import uvicorn

from __init__ import *



app = FastAPI()

#@app.get(conf["url_prefix"]+"/graphql")
@app.get("/download/cover/480x270_jpg/{_id}")
async def handle():
    return RedirectResponse("http://192.168.5.4:5666/test123",status_code=302)

@app.get("/download/avatar/256x256_jpg/{_id}")
async def handle():
    return RedirectResponse("http://192.168.5.4:5666/test123",status_code=302)

# For game data management
# User
import user.auth as auth
import user.profile as profile

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
            port = conf["ex_api_port"], 
            reload = conf["server_hot_reload"],
            ssl_keyfile = conf["https_key"], 
            ssl_certfile = conf["https_cert"]
        )
    else:
        uvicorn.run("main:app",
            host = "0.0.0.0", 
            port = conf["ex_api_port"], 
            reload = conf["server_hot_reload"]
        )
