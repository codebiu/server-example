# self
# from config.log import console
from config.fastapi_config import app
from service.user import UserService
from do.user import User, UserCreate

# lib
from fastapi.responses import JSONResponse
from fastapi import APIRouter, status

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, summary="添加用户返回id")
async def add(user: User) -> str:
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
