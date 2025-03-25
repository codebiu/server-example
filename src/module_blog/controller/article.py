# self
# from config.log import logger
from config.server import app
from ..service.article import ArticleService
from ..do.article import Article

# lib
from fastapi.responses import JSONResponse
from fastapi import APIRouter, status

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, summary="添加article返回id")
async def add(article: Article) -> str:
    return await ArticleService.add(article)


@router.delete("/")
async def delete(id: str):
    await ArticleService.delete(id)

@router.put("/")
async def update(article: Article):
    await ArticleService.update(article)


@router.get("/", status_code=status.HTTP_201_CREATED)
async def select(id: str) -> Article | None:
    return await ArticleService.select(id)


@router.get("/list", status_code=status.HTTP_201_CREATED)
async def list() -> list[Article]:
    return await ArticleService.list()

app.include_router(router, prefix="/article", tags=["article_tags"])
