# lib
import asyncio
from fastapi import APIRouter, status, UploadFile, File,HTTPException

# self
from config.server import app
# from config.log import logger # Placeholder for logger if needed

# Placeholder for future service/class imports
# from ..service.git_service import GitService
# from ..service.svn_service import SvnService
# from ..service.zip_service import ZipService

router = APIRouter()

@router.post("/upload_zip", summary="")
async def upload_zip(zip_source: ZipSource, upload_file: UploadFile):
    # 验证文件类型
    allowed_extensions = [".zip"]
    file_ext = upload_file.filename[upload_file.filename.rfind(".") :].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(400, detail="仅支持ZIP")

    return {
        "filename": upload_file.filename,
        "uuid": upload_file.file_uuid,
        "size": upload_file.size,  # 文件大小（字节）
    }


@router.post("/upload_svn", summary="初始化代码工程")
async def upload_svn(svn_source: SVNSource):
    pass
app.include_router(router, prefix="/project_source", tags=["Project Source Management"])