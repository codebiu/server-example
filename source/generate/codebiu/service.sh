# self
from do.template import Template
from dao.template import UserDao

# lib


class UserService:
    """template"""

    @staticmethod
    async def add(template: Template)->str:
        return await UserDao.add(template)

    @staticmethod
    async def delete(id: str):
        await UserDao.delete(id)

    @staticmethod
    async def update(template: Template):
        await UserDao.update(template)

    @staticmethod
    async def select(id: str) -> Template | None:
        return await UserDao.select(id)
    @staticmethod
    async def select_by_email(email: str) -> Template | None:
        return await UserDao.select_by_email(email)
    @staticmethod
    async def select_by_tel(tel: str) -> Template | None:
        return await UserDao.select_by_tel(tel)
    
    @staticmethod
    async def list() -> list[Template]:
        return await UserDao.list()
