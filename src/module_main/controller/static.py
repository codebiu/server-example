from config.path import project_path_base
from config.log import logger
from config.index import conf
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from config.server import app
############################### 静态首页 ##############################################
# html path 当前ip端口html路径
path_html = project_path_base / "source" / "html"
html_file = open(path_html / "index.html", "r", encoding="utf-8").read()


# 首页 app非router挂载
@app.get("/", response_class=HTMLResponse, summary="server首页html", tags=["base set"])
async def server():
    logger.info("初始首页html")
    return html_file


# 配置前端静态文件服务
app.mount(
    "/assets", StaticFiles(directory=path_html / "assets", html=True), name="assets"
)


############################### 自定义 Swagger #######################################
# 自定义 Swagger 文档路由，指向本地的 Swagger UI 文件
@app.get("/docs_local", include_in_schema=False, tags=["base set"])
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_js_url="/assets/swagger-ui/swagger-ui-bundle.js",
        swagger_css_url="/assets/swagger-ui/swagger-ui.css",
    )
