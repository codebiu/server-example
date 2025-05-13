import json
from fastapi import File, UploadFile, APIRouter
from config.server import app
from module_main.service.file import fileService

router = APIRouter()


@router.post("/upload", summary="上传文件")
async def upload(file: UploadFile = File(...)):
    return await fileService.upload_file(file)

@router.post("/upload_trunks", summary="分片上传文件")
async def upload_trunks(offset: int, total_size: int, file: UploadFile = File(...)):
    return await fileService.upload_file_trunks(offset, total_size,file)


@router.get("/tree", summary="获取目录树")
def tree(dir: str):
    tree = fileService.get_directory_tree(dir)
    return tree


@router.get("/open", summary="获取文件")
async def open(file: str):
    return await fileService.open_file(file)


@router.get("/open_stream", summary="分片流式获取文件")
async def open_stream(file: str):
    return await fileService.open_file_stream(file)





app.include_router(router, prefix="/utils", tags=["utils"])
