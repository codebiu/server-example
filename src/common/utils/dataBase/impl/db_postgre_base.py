from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from common.utils.dataBase.do.db_config import PostgresConfig
from common.utils.dataBase.interface.db_base_interface import DBBaseInterface


class DBPostgreBase(DBBaseInterface):

    session_factory: sessionmaker = None
    engine: create_async_engine = None
    url: str | None = None

    def __init__(self, postgresConfig: PostgresConfig):
        type = "postgresql+asyncpg"
        # postgresql+asyncpg://hero:heroPass123@0.0.0.0:5432/heroes_db
        self.url = f"{type}://{postgresConfig.user}:{postgresConfig.password}@{postgresConfig.host}:{postgresConfig.port}/{postgresConfig.database}"

    def connect(self):
        """建立数据库连接"""
        self.engine = create_async_engine(self.url, echo=True)
        self.session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    async def is_connected(self):
        """检查连接状态"""
        return bool(self.engine and not await self.engine.dispose())

    async def reconnect(self):
        """重新连接数据库"""
        await self.disconnect()
        self.connect()

    async def disconnect(self):
        """断开数据库连接"""
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.session_factory = None

    async def get_info(self):
        """获取数据库信息"""
        return {
            "type": "PostgreSQL",
            "url": self.url,
            "connected": await self.is_connected(),
            "tables": await self._get_table_list(),
        }

    async def get_session(self):
        """获取异步会话"""
        session = self.session_factory()
        try:
            yield session
        finally:
            await session.close()

    async def create_all(self, models):
        """创建所有表结构"""
        async with self.engine.begin() as conn:
            await conn.run_sync(
                lambda sync_conn: [
                    model.metadata.create_all(sync_conn) for model in models
                ]
            )

    async def execute(self, sql):
        """执行原生SQL

        Args:
            sql: SQL语句

        Returns:
            SELECT 返回结果列表，其他操作返回影响行数
        """
        async with self.session_factory() as session:
            result = await session.execute(text(sql))
            await session.commit()

            if sql.strip().upper().startswith("SELECT"):
                return result.fetchall()
            return result.rowcount

    async def _get_table_list(self):
        """获取所有表名 (内部方法)"""
        if not await self.is_connected():
            return []

        sql = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        """
        tables = await self.execute(sql)
        # 去除""
        result = []
        for table in tables:
            if table[0]:
                result.append(table[0])
        return result
