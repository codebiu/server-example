from pathlib import Path


class CodebiuGenerate:
    """代码生成器"""

    def create(self, data: dict):
        """生成代码"""
        base_path = Path("todo")
        # 基础对象名和驼峰
        name_snake = "test_generate"
        name_camel = CodebiuGenerate.snake_to_camel(name_snake)

        #
        controller = {
            "file_name": name_snake + ".py",
            "content": f"""
from config.fastapi_config import app
from service.user import UserService
from do.user import User, UserCreate

# lib
from fastapi.responses import JSONResponse
from fastapi import APIRouter, status

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, summary="添加用户返回id")
async def add(user: UserCreate) -> str:
    return await UserService.add(user)


@router.delete("/")
async def delete(id: str):
    await UserService.delete(id)


@router.put("/")
async def update(user: User):
    await UserService.update(user)


@router.get("/", status_code=status.HTTP_201_CREATED)
async def select(id: str) -> User | None:
    return await UserService.select(id)


@router.get("/list", status_code=status.HTTP_201_CREATED)
async def list() -> list[User]:
    return await UserService.list()

app.include_router(router, prefix="/user", tags=["用户"])
                        """,
        }

        service = {
            "file_name": name_snake + ".py",
            "content": f"""

                        from pydantic import BaseModel
                        from typing import Optional

                        class {name_camel}Controller:
                            name: str   
                     """,
        }

        name_controller_class = name_camel + "Controller"

        name_service_class = name_camel + "Service"
        name_do_class = name_camel + "DO"
        name_dao_class = name_camel + "DAO"

        # 基础文件夹
        folder_path_base = Path(name_snake)
        folder_path_base_full = base_path / folder_path_base
        # 创建文件夹（如果它不存在的话）
        folder_path_base_full.mkdir(parents=True, exist_ok=True)

        # 创建name_snake文件夹 在文件下建立文件和文件
        # 定义文件夹和文件的路径

        # 创建文件并写入内容
        with file_path.open("w") as file:
            file.write("Hello, this is a test file inside the created folder.")

    def snake_to_camel(snake_str):
        # 分割字符串，转换成驼峰
        components = snake_str.split("_")
        # 将第一个单词保持小写，后面的单词首字母大写
        return components[0] + "".join(x.title() for x in components[1:])
