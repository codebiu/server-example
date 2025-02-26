import json
from fastapi import File, UploadFile, APIRouter
from config.server import app
from module_main.service.file import fileService

router = APIRouter()


@router.post("/file", summary="上传音频文件")
async def upload_file(file: UploadFile = File(...)):
    pass


app.include_router(router, prefix="/audio", tags=["音频处理"])