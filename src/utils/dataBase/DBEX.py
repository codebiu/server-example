from fastapi import APIRouter, HTTPException, Request, status
from sqlmodel.ext.asyncio.session import AsyncSession
from config.db import Data, DataNoCommit
import sqlmodel


class DBExtentiontentionBase:
    def controller_init(routerThis, description, Do, DoCreate,DoUpdate) -> str:
        class DaoSelf:
            """test"""

        DBExtentiontentionBase.dao_init(DaoSelf,Do, DoCreate,DoUpdate)

        @routerThis.post(
            "/default",
            status_code=status.HTTP_201_CREATED,
            summary=f"添加{description}返回id",
        )
        async def add(do: DoCreate) -> str:
            return await DaoSelf.add(do)

        @routerThis.delete(
            "/default",
            summary=f"删除{description}",
        )
        async def delete(id: str):
            return await DaoSelf.delete(id)

        @routerThis.put(
            "/default",
            summary=f"更新{description}",
        )
        async def update(do: Do):
            await DaoSelf.update(do)

        @routerThis.get(
            "/default",
            status_code=status.HTTP_201_CREATED,
            summary=f"获取单个{description}",
        )
        async def select(id: str) -> Do | None:
            return await DaoSelf.select(id)

        @routerThis.get(
            "/default/list",
            status_code=status.HTTP_201_CREATED,
            summary=f"获取批量{description}",
        )
        async def list():
            return await DaoSelf.list()

    def dao_init(DoDao,Do, DoCreate,DoUpdate):

        @DataNoCommit
        async def add(do: DoCreate, session=AsyncSession) -> str:
            """插入一个新的do  无需显式调用 session.commit()，因为装饰器已经处理了"""
            db_do = Do.model_validate(do)
            session.add(db_do)
            await session.commit()
            return db_do.id

        @Data
        async def delete(id: str, session=AsyncSession):
            db_do = await session.get(Do, id)
            return await session.delete(db_do)

        @Data
        async def update(do: DoUpdate, session=AsyncSession):
            """更新用户信息"""
            do_to_upadte: Do = await session.get(Do, do.id)
            # do_to_upadte.key = do.key
            # do_to_upadte.value = do.value
            # do_to_upadte.update_at = do.update_at
            """动态赋值"""
            do_dict = do.dict()
            for key, value in do_dict.items():
                # print(f"{key}: {value}")
                # print(getattr(do_to_upadte, key, 'None'))
                if key != "id":
                    setattr(do_to_upadte, key, value)
            session.add(do_to_upadte)
            await session.commit()  # 提交事务
            # session.refresh刷新可以保存并行数据更新问题,实时性要求不高的可以禁用来提升性能
            await session.refresh(do_to_upadte)
            return do_to_upadte

        @DataNoCommit
        async def select(id: str, session=AsyncSession) -> Do | None:
            return await session.get(Do, id)

        @DataNoCommit
        async def list(session=AsyncSession) -> any:
            result = await session.exec(sqlmodel.select(Do))
            users = result.all()
            return users

        if DoDao != None:
            DoDao.add = add
            DoDao.delete = delete
            DoDao.update = update
            DoDao.select = select
            DoDao.list = list


class DBExtention(DBExtentiontentionBase):
    def controller_init(
        routerThis, description, DoService, Do, DoCreate, DoUpdate
    ) -> str:
        @routerThis.post(
            "/default",
            status_code=status.HTTP_201_CREATED,
            summary=f"添加{description}返回id",
        )
        async def add(do: DoCreate) -> str:
            return await DoService.add(do)

        @routerThis.delete(
            "/default",
            summary=f"删除{description}",
        )
        async def delete(id: str):
            return await DoService.delete(id)

        @routerThis.put(
            "/default",
            summary=f"更新{description}",
        )
        async def update(do: DoUpdate):
            await DoService.update(do)

        @routerThis.get(
            "/default",
            status_code=status.HTTP_201_CREATED,
            summary=f"获取单个{description}",
        )
        async def select(id: str) -> Do | None:
            return await DoService.select(id)

        @routerThis.get(
            "/default/list",
            status_code=status.HTTP_201_CREATED,
            summary=f"获取批量{description}",
        )
        async def list():
            return await DoService.list()

    # service初始化
    def service_init(DoService, DoDao, Do, DoCreate, DoUpdate):
        @staticmethod
        async def add(do: DoCreate) -> str:
            return await DoDao.add(do)

        DoService.add = add

        @staticmethod
        async def delete(id: str):
            await DoDao.delete(id)

        DoService.delete = delete

        @staticmethod
        async def update(do: DoUpdate):
            await DoDao.update(do)

        DoService.update = update

        @staticmethod
        async def select(id: str) -> Do | None:
            return await DoDao.select(id)

        DoService.select = select

        @staticmethod
        async def list():
            return await DoDao.list()

        DoService.list = list

    # def dao_init(DoDao, Do, DoCreate, DoUpdate):

    #     @DataNoCommit
    #     async def add(do: DoCreate, session=AsyncSession) -> str:
    #         """插入一个新的do  无需显式调用 session.commit()，因为装饰器已经处理了"""
    #         db_do = Do.model_validate(do)
    #         session.add(db_do)
    #         await session.commit()
    #         return db_do.id

    #     DoDao.add = add

    #     @Data
    #     async def delete(id: str, session=AsyncSession):
    #         db_do = await session.get(Do, id)
    #         return await session.delete(db_do)

    #     DoDao.delete = delete

    #     @Data
    #     async def update(do: DoUpdate, session=AsyncSession):
    #         """更新用户信息"""
    #         do_to_upadte: Do = await session.get(Do, do.id)
    #         # do_to_upadte.key = do.key
    #         # do_to_upadte.value = do.value
    #         # do_to_upadte.update_at = do.update_at
    #         """动态赋值"""
    #         do_dict = do.dict()
    #         for key, value in do_dict.items():
    #             # print(f"{key}: {value}")
    #             # print(getattr(do_to_upadte, key, 'None'))
    #             if key != "id":
    #                 setattr(do_to_upadte, key, value)
    #         session.add(do_to_upadte)
    #         await session.commit()  # 提交事务
    #         # session.refresh刷新可以保存并行数据更新问题,实时性要求不高的可以禁用来提升性能
    #         await session.refresh(do_to_upadte)
    #         return do_to_upadte

    #     DoDao.update = update

    #     @DataNoCommit
    #     async def select(id: str, session=AsyncSession) -> Do | None:
    #         return await session.get(Do, id)

    #     DoDao.select = select

    #     @DataNoCommit
    #     async def list(session=AsyncSession) -> any:
    #         result = await session.exec(sqlmodel.select(Do))
    #         users = result.all()
    #         return users

    #     DoDao.list = list
