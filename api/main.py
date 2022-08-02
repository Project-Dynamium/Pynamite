from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, FileResponse, Response
import uvicorn

from __init__ import *

if conf["debug"]:
    app = FastAPI()
else:
    app = FastAPI(docs_url=None, redoc_url=None)

import user.auth as auth
import user.profile as profile
import res.download as download
import res.info as chart_info
import time, random

# For game resource distribution
# Public distribute
@app.get("/download/avatar/256x256_jpg/{_id}")
async def handle():
    return RedirectResponse("http://127.0.0.1:10442/")

# Local distribute
    
@app.get("/download/{info:path}")
async def local_cover_distribute(request: Request, info: str):
    result = await auth.in_game_check_login(request.headers.get("x-soudayo"))
    if result == 403:
        return Response(content="Invalid token.", status_code=403)

    info = info.split("/")
    if info[-1][2:7] == "local" and info[-1][0] == "0":
        #del info[-2]
        local_ip = (await profile.get_user_info(result["_id"]))["local_ip"]
        return RedirectResponse("http://{}:10442/{}".format(local_ip,"/".join(info)),status_code=302)

    id = info[-1]
    del info[-1]
    res_type = "/".join(info)

    r = {"status":404}
    if res_type == "music/encoded":
        r = download.get_download_link("set/{}/{}m.mp3.rnx".format(id,id))
    elif res_type == "cover/encoded":
        r = download.get_download_link("set/{}/{}c.jpg.rnx".format(id,id))
    elif res_type == "preview/encoded":
        r = download.get_download_link("set/{}/{}p.mp3.rnx".format(id,id))
    elif res_type == "chart/encoded":
        try:
            r = download.get_download_link("set/{}/{}.xml.rnx".format(await chart_info.get_chart_set(id),id))
        except Exception as e:
            real_id = id.split(";")[0]
            r = download.get_download_link("set/{}/{}.xml.rnx".format(await chart_info.get_chart_set(real_id),real_id))
    #elif res_type == "cover/480x270_jpg":
    #   r = download.get_download_link("cover_480x270_jpg/{}.jpg".format(id),pic=True)"""
    elif res_type == "cover/480x270_jpg":
        try:
            info = (await chart_info.get_set_chart(id))["cover_preview"]
            url = info[random.randint(0,len(info)-1)]
            return RedirectResponse(url,status_code=302)
        except:
            Response(status_code=403)
        #return RedirectResponse("https://cdn2.terrace.ink/download/cover/480x270_jpg/"+id,status_code=302)
    elif res_type == "avatar/256x256_jpg":
        r = download.get_download_link("avatar/{}.jpg".format(id))
    

    return RedirectResponse(r["result"],status_code=302) if r["status"] == 200 \
            else Response(status_code=r["status"] )

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
