# self
# from config.log import console
from config.fastapi_config import app
from service.template import TemplateService
from do.template import Template, TemplateCreate

# lib
from fastapi.responses import JSONResponse
from fastapi import APIRouter, status

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, summary="添加用户返回id")
async def add(template: Template) -> str:
    return await TemplateService.add(template)


@router.delete("/")
async def delete(id: str):
    await TemplateService.delete(id)

@router.put("/")
async def update(template: Template):
    await TemplateService.update(template)


@router.get("/", status_code=status.HTTP_201_CREATED)
async def select(id: str) -> Template | None:
    return await TemplateService.select(id)


@router.get("/list", status_code=status.HTTP_201_CREATED)
async def list() -> list[Template]:
    return await TemplateService.list()

app.include_router(router, prefix="/template", tags=["template_tags"])
