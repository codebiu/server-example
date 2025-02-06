# self
from do.$template_name import $TemplateName
from dao.$template_name import UserDao

# lib


class UserService:
    """$template_name"""

    @staticmethod
    async def add($template_name: $TemplateName)->str:
        return await UserDao.add($template_name)

    @staticmethod
    async def delete(id: str):
        await UserDao.delete(id)

    @staticmethod
    async def update($template_name: $TemplateName):
        await UserDao.update($template_name)

    @staticmethod
    async def select(id: str) -> $TemplateName | None:
        return await UserDao.select(id)
    @staticmethod
    async def select_by_email(email: str) -> $TemplateName | None:
        return await UserDao.select_by_email(email)
    @staticmethod
    async def select_by_tel(tel: str) -> $TemplateName | None:
        return await UserDao.select_by_tel(tel)
    
    @staticmethod
    async def list() -> list[$TemplateName]:
        return await UserDao.list()
