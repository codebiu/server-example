from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

# self
from config.db import Dao
from module_todo.do.test import Test, TestUpdate


class TestDao:
    def __init__(self, session: AsyncSession = None):
        self.session = session

    @Dao
    async def add(self, Test: Test) -> str:
        self.session.add(Test)
        await self.session.flush()
        return Test.id

    async def delete(self, id: str) -> None:
        Test = await self.session.get(Test, id)
        if Test:
            await self.session.delete(Test)

    async def update(self, id: str, Test_update: TestUpdate) -> Test | None:
        Test = await self.session.get(Test, id)
        if Test:
            for key, value in Test_update.dict(exclude_unset=True).items():
                setattr(Test, key, value)
            self.session.add(Test)
        return Test

    @Dao
    async def select(self, id: str) -> Test | None:
        return await self.session.get(Test, id)

    async def list(self) -> list[Test]:
        result = await self.session.exec(select(Test))
        Tests = result.all()
        return Tests


if __name__ == "__main__":
    import asyncio
    from module_main.dao.db import TableDao

    async def main():
        await TableDao.create()
        testDao = TestDao()
        id = await testDao.add(Test(content="test"))
        print(id)
        test = await testDao.select(id)
        print(test)
        id2 = await testDao.add(Test(content="test1"))
        print(id2)

    # asyncio.run()会自动关闭循环 报错
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
