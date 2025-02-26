# self
from config.log import logger
from config.server import app
from config.index import conf
# from module_main.controller import *
from module_todo.controller import *
# lib
logger.info("ok...基础依赖全部")
logger.info('%s%s', "server:http://127.0.0.1:", str(conf["server"]["port"]))
logger.info('%s%s%s', "docs:http://127.0.0.1:", str(conf["server"]["port"]),'/docs')
if __name__ == "__main__":
    # print("pc_main", path.path_html, __name__)
    # 发布时server  开发时在.vscode目录下launch.json配置
    import uvicorn
    # uvicorn.run(app, host="127.0.0.1", port=1666)
    uvicorn.run(
        "server_main:app",
        host=conf["server"]["host"],
        port=conf["server"]["port"],
        # lsp 需要关闭reload
        # 导致默认的 ProactorEventLoop 在 Windows 上更改为 SelectorEventLoop,lsp调试服务无法正常开启
        reload=True,
    )
    # uvicorn.run(
    #     "server_main:app",
    #     host=conf["server"]["host"],
    #     port=conf["server"]["port"],
    #     workers=1,
    # )
    # gunicorn server_main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:1888
    
    