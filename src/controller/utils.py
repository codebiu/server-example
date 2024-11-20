import json
from fastapi import File, UploadFile, APIRouter
from config.fastapi_config import app
from service.fileService import fileService

router = APIRouter()


@router.post("/upload", summary="上传文件")
async def upload_file(file: UploadFile = File(...)):
    return await fileService.upload_file(file)


@router.get("/tree", summary="获取目录树")
def upload_file(dir: str):
    tree = fileService.get_directory_tree(dir)
    return tree


@router.get("/open", summary="获取文件")
async def upload_file(file: str):
    return await fileService.open_file(file)

@router.get("/open_stream", summary="分片流式获取文件")
async def upload_file(file: str):
    return await fileService.open_file_stream(file)


app.include_router(router, prefix="/utils", tags=["utils"])
