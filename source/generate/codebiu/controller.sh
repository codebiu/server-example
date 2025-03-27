# self
# from config.log import logger
from config.server import app
from ..service.$template_name import $TemplateNameService
from ..do.$template_name import $TemplateName

# lib
from fastapi.responses import JSONResponse
from fastapi import APIRouter, status

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, summary="添加$template_name返回id")
async def add($template_name: $TemplateName) -> str:
    return await $TemplateNameService.add($template_name)


@router.delete("/")
async def delete(id: str):
    await $TemplateNameService.delete(id)

@router.put("/")
async def update($template_name: $TemplateName):
    await $TemplateNameService.update($template_name)


@router.get("/", status_code=status.HTTP_201_CREATED)
async def select(id: str) -> $TemplateName | None:
    return await $TemplateNameService.select(id)


@router.get("/list", status_code=status.HTTP_201_CREATED)
async def list() -> list[$TemplateName]:
    return await $TemplateNameService.list()

app.include_router(router, prefix="/$template_name", tags=["$template_name_tags"])
