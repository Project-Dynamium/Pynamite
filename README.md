# Pynamite
A game server for the game Dynamite, written by Python.   
用 Python 实现的 Dynamite 游戏服务器，全异步
# Detail
## game
Dynamite 游戏服务器后端  
使用 FastAPI 搭建网络服务器，使用 strawberry 处理 graphql 请求，使用 motor 操作 MongoDB
## api
游戏服务器对外接口，主要负责资源分发与上传以及数据管理  
使用 FastAPI 实现