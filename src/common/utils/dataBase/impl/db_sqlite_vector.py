from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
# 防止注入
from sqlalchemy import text
from common.utils.dataBase.interface.db_base_interface import DBBaseInterface

class DBSqliteBase(DBBaseInterface):
    url = None
    engine = None
    sessionFactory = None

    def __init__(self, path: str):
        type = "sqlite+aiosqlite"
        self.url = f"{type}:///{path}"

    def connect(self):
        self.engine = create_async_engine(self.url, echo=True)
        self.sessionFactory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    def disconnect(self):
        print("sqlite disconnect")

    async def get_session(self):
        async with self.sessionFactory() as session:
            yield session

    async def create_all(self, models: list) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(lambda sync_conn: [model.metadata.create_all(sync_conn) for model in models])

    async def execute(self, sql: str, params: dict | None = None):
        """执行原生SQL语句
        Args:
            sql: SQL语句，可以使用 :param 形式参数
            params: 参数字典
        Returns:
            对于SELECT返回结果列表，其他操作返回影响行数
        """
        async with self.sessionFactory() as session:
            result = await session.execute(text(sql), params or {})
            await session.commit()
            
            if sql.strip().upper().startswith("SELECT"):
                return [dict(row._mapping) for row in result]
            return result.rowcount