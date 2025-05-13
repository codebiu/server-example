# self
from ..do.$template_name import $TemplateName
from ..dao.$template_name import $TemplateNameDao

# lib


class $TemplateNameService:
    """$template_name"""

    @staticmethod
    async def add($template_name: $TemplateName)->str:
        return await $TemplateNameDao.add($template_name)

    @staticmethod
    async def delete(id: str):
        await $TemplateNameDao.delete(id)

    @staticmethod
    async def update($template_name: $TemplateName):
        await $TemplateNameDao.update($template_name)

    @staticmethod
    async def select(id: str) -> $TemplateName | None:
        return await $TemplateNameDao.select(id)
    @staticmethod
    async def select_by_email(email: str) -> $TemplateName | None:
        return await $TemplateNameDao.select_by_email(email)
    @staticmethod
    async def select_by_tel(tel: str) -> $TemplateName | None:
        return await $TemplateNameDao.select_by_tel(tel)
    
    @staticmethod
    async def list() -> list[$TemplateName]:
        return await $TemplateNameDao.list()
