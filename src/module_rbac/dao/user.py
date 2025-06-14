from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

# self
from config.db import Data,DataNoCommit
from module_main.do.user import User,UserCreate, UserLogin, UserPublic


class UserDao:

    @DataNoCommit
    async def add(user: User, session=AsyncSession) -> str:
        """插入一个新的用户  无需显式调用 session.commit()，因为装饰器已经处理了"""
        db_user = User.model_validate(user)
        session.add(db_user)
        await session.commit()  # 提交事务
        # await session.refresh(db_user)  # 刷新数据
        # 显示刷新  数据锁和同步问题
        return db_user.id

    @Data
    async def delete(id: str, session=AsyncSession):
        hero = await session.get(User, id)
        return await session.delete(hero)

    @Data
    async def update(user: User, session=AsyncSession):
        """更新用户信息"""
        user_to_upadte:User = await session.get(User, user.id)
        user_to_upadte.name = user.name
        user_to_upadte.email = user.email
        session.add(user_to_upadte)
        await session.commit()  # 提交事务
        session.refresh(user_to_upadte)
        return user_to_upadte

    @DataNoCommit
    async def select(id: str, session=AsyncSession) -> User | None:
        return await session.get(User, id)
    
    @DataNoCommit
    async def select_by_email(email: str, session=AsyncSession) -> User | None:
        query = select(User).where(User.email == email)
        result = await session.exec(query)
        user = result.first()  # 直接使用 .first() 获取第一个结果或 None
        return user
    
    @DataNoCommit
    async def select_by_tel(tel: str, session=AsyncSession) -> User | None:
        query = select(User).where(User.tel == tel)
        result = await session.exec(query)
        user = result.first()  # 直接使用 .first() 获取第一个结果或 None
        return user

    @DataNoCommit
    async def list(session=AsyncSession) -> list[User]:
        result = await session.exec(select(User))
        users = result.all()
        return users

        # 快捷方式 id
        # sql = select(User).where(User.id == id)
        # print(sql) # 这里可以打印出sql
        # result = await session.execute(sql)
        # data = result.scalars().first()
