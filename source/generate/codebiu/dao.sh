from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

# self
from config.db import Data,DataNoCommit
from do.$template_name import $TemplateName,$TemplateNameCreate, $TemplateNameLogin, $TemplateNamePublic


class $TemplateNameDao:

    @DataNoCommit
    async def add($template_name: $TemplateName, session=AsyncSession) -> str:
        """插入一个新的用户  无需显式调用 session.commit()，因为装饰器已经处理了"""
        db_$template_name = $TemplateName.model_validate($template_name)
        session.add(db_$template_name)
        await session.commit()  # 提交事务
        # await session.refresh(db_$template_name)  # 刷新数据
        # 显示刷新  数据锁和同步问题
        return db_$template_name.id

    @Data
    async def delete(id: str, session=AsyncSession):
        hero = await session.get($TemplateName, id)
        return await session.delete(hero)

    @Data
    async def update($template_name: $TemplateName, session=AsyncSession):
        """更新用户信息"""
        $template_name_to_upadte:$TemplateName = await session.get($TemplateName, $template_name.id)
        $template_name_to_upadte.name = $template_name.name
        $template_name_to_upadte.email = $template_name.email
        session.add($template_name_to_upadte)
        await session.commit()  # 提交事务
        session.refresh($template_name_to_upadte)
        return $template_name_to_upadte

    @DataNoCommit
    async def select(id: str, session=AsyncSession) -> $TemplateName | None:
        return await session.get($TemplateName, id)
    
    @DataNoCommit
    async def list(session=AsyncSession) -> list[$TemplateName]:
        result = await session.exec(select($TemplateName))
        $template_names = result.all()
        return $template_names
