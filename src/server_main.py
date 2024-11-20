# self
from config.log import console
from config.fastapi_config import app
from config.index import conf

# import config
from config import db, fastapi_config, path, log, index
from controller import index, user, utils, ws, test0,dict

print("test")
# lib


console.log("...依赖引入完成")

if __name__ == "__main__":
    # print("pc_main", path.path_html, __name__)
    # 发布时server  开发时在.vscode目录下launch.json配置
    import uvicorn

    console.log("server:starting port http://127.0.0.1:" + str(conf["server"]["port"]))
    # uvicorn.run(app, host="127.0.0.1", port=1666)
    uvicorn.run(
        "server_main:app",
        host=conf["server"]["host"],
        port=conf["server"]["port"],
        reload=True,
    )
    # uvicorn.run(
    #     "server_main:app",
    #     host=conf["server"]["host"],
    #     port=conf["server"]["port"],
    #     workers=1,
    # )
    # gunicorn server_main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:1888