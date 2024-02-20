# Pynamite
# Deprecation Warning: 本项目因代码质量和其它原因，已停止维护，如非必要请使用其它实现。
A game server for the game Dynamite, written by Python.   
用 Python 实现的 Dynamite 游戏服务器，全异步
# Detail
## game
Dynamite 游戏服务器后端  
使用 FastAPI 搭建网络服务器，使用 strawberry 处理 graphql 请求，使用 motor 操作 MongoDB
## api
游戏服务器对外接口，主要负责资源分发与上传以及数据管理  
使用 FastAPI 实现，使用 motor 操作 MongoDB
# Setup
1. 安装 Python >= 3.7  
2. `git clone` 或者 `Download zip` 下载项目源码  
3. `pip install -i requirements.txt`  
4. 将项目文件中名称为 `*_sample.xxx`的文件重命名为 `*.xxx`，并根据自己需要修改其中内容  
5. 打开两个 shell ，分别运行 `game` 和 `api` 目录下的 `main.py` 文件  
