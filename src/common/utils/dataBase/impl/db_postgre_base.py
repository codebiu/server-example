from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import delete, update, text
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

#
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

    async def exec(self, sql, session: AsyncSession = None):
        """执行原生SQL（支持外部传入session以支持事务）

        Args:
            sql: SQL语句
            session: 可选的AsyncSession对象，如果不传则自动创建新会话

        Returns:
            SELECT 返回结果列表，其他操作返回影响行数
        """
        # 判断是否需要自动管理session生命周期
        should_close_session = False
        if session is None:
            session = self.session_factory()
            should_close_session = True

        try:
            result = await session.exec(text(sql))

            # 只有自动创建的session才需要commit
            if should_close_session:
                await session.commit()

            # 处理返回结果
            if sql.strip().upper().startswith("SELECT"):
                return result.fetchall()
            return result.rowcount

        finally:
            # 确保自动创建的session被关闭
            if should_close_session:
                await session.close()

    async def _get_table_list(self, table_schema="public"):
        """获取所有表名 (内部方法)"""
        if not await self.is_connected():
            return []

        sql = f"""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = '{table_schema}'
        """
        tables = await self.exec(sql)
        # 去除""
        result = []
        for table in tables:
            if table[0]:
                result.append(table[0])
        return result

    async def delete(self, model, condition, session):
        """基础删除方法"""
        statement = delete(model).where(condition)
        result = await session.exec(statement)
        await session.commit()
        if result.rowcount > 0:
            print(f"已删除 {result.rowcount} 条记录")
        else:
            print("删除 未找到匹配的记录")
        return result

    async def delete_id(self, model, id, session):
        """删除方法"""
        statement = delete(model).where(model.id == id)
        result = await session.exec(statement)
        await session.commit()
        if result.rowcount > 0:
            print(f"已删除 {result.rowcount} 条记录")
        else:
            print("删除 未找到匹配的记录")
        return result

    async def upsert(self, model, data, session):
        """更新或插入数据（排除未设置的字段)"""
        update_data = data.model_dump(exclude_unset=True)

        # 先尝试更新
        result = await session.exec(
            update(model).where(model.id == data.id).values(**update_data)
        )

        # 如果未更新则插入
        if result.rowcount == 0:
            session.add(data)

        await session.commit()

    async def upsert_batch(self, model, data_list, session):
        """
        通用的批量插入/更新方法
        适用于大多数SQL数据库（不依赖特定数据库功能）

        参数:
            model: SQLModel 表模型类
            data_list: 要插入/更新的模型实例列表
            session: 数据库会话
        """
        if not data_list:
            return
        # 分批处理
        to_insert_dict = {}
        for data in data_list:
            update_data = data.model_dump(exclude_unset=True)
            # 先尝试更新
            result = await session.exec(
                update(model).where(model.id == data.id).values(**update_data)
            )
            # 如果未更新则记录等待插入
            if result.rowcount == 0:
                to_insert_dict[data.id] = data

        # 批量插入
        if to_insert_dict:
            to_insert_list = list(to_insert_dict.values())
            session.add_all(to_insert_list)

        await session.commit()


if __name__ == "__main__":
    # 配置
    from config.index import conf

    db_config = conf["database.postgresql"]
    postgresConfig: PostgresConfig = PostgresConfig(**db_config)

    async def main():
        db_posgre = DBPostgreBase(postgresConfig)
        db_posgre.connect()
        list_table = await db_posgre._get_table_list()
        print(list_table)

    import asyncio

    asyncio.run(main())
