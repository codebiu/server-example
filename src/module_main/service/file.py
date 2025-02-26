from pathlib import Path
import aiofiles
import mimetypes
from fastapi import File, Response, UploadFile, APIRouter
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
import shutil
from config.path import dir_uploaded
from common.utils.file.directory_tree import DirectoryTree
from common.utils.file.file_utils import FileUtils




class fileService:
    """文件服务"""

    @staticmethod
    async def upload_file(
        file_upload: UploadFile = File(...), upload_folder=dir_uploaded
    ):
        """上传文件"""
        try:
            upload_folder = Path(upload_folder)
            # 检查上传文件夹是否存在，如果不存在则创建
            if not upload_folder.exists():
                upload_folder.mkdir(parents=True, exist_ok=True)
            # 将文件保存到本地
            file_location = upload_folder / file_upload.filename
            # with open(file_location, "wb") as buffer:
            #     shutil.copyfileobj(file.file, buffer)
            async with aiofiles.open(file_location, "wb") as buffer:
                await buffer.write(file_upload.file.read())

            return JSONResponse(
                status_code=200,
                content={
                    "message": "File uploaded successfully",
                    "file_path": str(file_location),
                },
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"message": "Failed to upload file", "error": str(e)},
            )
            
    @staticmethod
    async def upload_file_trunks(
        file_upload: UploadFile = File(...), upload_folder=dir_uploaded
    ):
        """TODO 分片上传文件 """
        pass
        # try:
        #     # 以追加模式打开文件
        #     async with aiofiles.open(file_path, mode="ab") as f:
        #         # 将当前分块写入文件
        #         while chunk := await file.read(1024 * 1024):  # 每次读取 1MB
        #             await f.write(chunk)
        # except Exception as e:
        #     raise JSONResponse(status_code=500, detail=f"Error writing file: {e}")

        # # 使用 pathlib 获取文件大小
        # current_size = file_path.stat().st_size
        # if current_size >= total_size:
        #     return {"message": "Upload complete", "file_path": str(file_path)}
        # else:
        #     return {"message": "Chunk uploaded", "offset": current_size}

    # 根据路径获取目录树和文件信息
    @staticmethod
    def get_directory_tree(file_path: str, upload_folder=dir_uploaded):
        upload_folder = Path(upload_folder)
        # 实际存储路径
        current_dir = upload_folder / file_path
        directory_tree = DirectoryTree.build_directory_tree(current_dir)
        return directory_tree
    
    # 根据路径获取单层目录树和文件信息
    @staticmethod
    def get_dirFile_level_one(file_path: str, upload_folder=dir_uploaded):
        upload_folder = Path(upload_folder)
        # 实际存储路径
        current_dir = upload_folder / file_path
        directory_tree = DirectoryTree.build_dirFile_level_one(current_dir)
        return directory_tree
    

    # 根据路径流式打开文件获取内容
    @staticmethod
    async def open_file_stream(filename: str, upload_folder=dir_uploaded):
        """打开文件"""
        upload_folder = Path(upload_folder)
        # 实际存储路径
        current_path = upload_folder / filename
        try:
            if not current_path.exists():
                return Response(status_code=404, content="File not found")
            # 确定文件的 MIME 类型
            content_type, _ = mimetypes.guess_type(current_path)
            if content_type is None:
                content_type = "application/octet-stream"  # 默认为二进制流
            content = FileUtils.read_file_stream(current_path)
            return StreamingResponse(
                content,
                media_type=content_type,
                headers={
                    # 设置 Content-Disposition 为 inline 以允许浏览器预览
                    "Content-Disposition": f"inline; filename={filename}"
                },
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"message": "Failed to open file", "error": str(e)},
            )

    

    # 根据路径打开文件获取内容
    @staticmethod
    async def open_file(filename: str, upload_folder=dir_uploaded):
        """打开文件"""
        upload_folder = Path(upload_folder)
        # 实际存储路径
        current_path = upload_folder / filename
        try:
            if not current_path.exists():
                return Response(status_code=404, content="File not found")
            # 确定文件的 MIME 类型
            content_type, _ = mimetypes.guess_type(current_path)
            if content_type is None:
                content_type = "application/octet-stream"  # 默认为二进制流
            headers={
                    # 设置 Content-Disposition 为 inline 以允许浏览器预览
                    "Content-Disposition": f"inline; filename={filename}"
                }
            return FileResponse(path=current_path, media_type=content_type, headers=headers)
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"message": "Failed to open file", "error": str(e)},
            )

