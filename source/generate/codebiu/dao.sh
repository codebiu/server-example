from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

# self
from config.db import Data,DataNoCommit
from do.template import Template,TemplateCreate, TemplateLogin, TemplatePublic


class TemplateDao:

    @DataNoCommit
    async def add(template: Template, session=AsyncSession) -> str:
        """插入一个新的用户  无需显式调用 session.commit()，因为装饰器已经处理了"""
        db_template = Template.model_validate(template)
        session.add(db_template)
        await session.commit()  # 提交事务
        # await session.refresh(db_template)  # 刷新数据
        # 显示刷新  数据锁和同步问题
        return db_template.id

    @Data
    async def delete(id: str, session=AsyncSession):
        hero = await session.get(Template, id)
        return await session.delete(hero)

    @Data
    async def update(template: Template, session=AsyncSession):
        """更新用户信息"""
        template_to_upadte:Template = await session.get(Template, template.id)
        template_to_upadte.name = template.name
        template_to_upadte.email = template.email
        session.add(template_to_upadte)
        await session.commit()  # 提交事务
        session.refresh(template_to_upadte)
        return template_to_upadte

    @DataNoCommit
    async def select(id: str, session=AsyncSession) -> Template | None:
        return await session.get(Template, id)
    
    @DataNoCommit
    async def list(session=AsyncSession) -> list[Template]:
        result = await session.exec(select(Template))
        templates = result.all()
        return templates
