from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
# 防止注入
from sqlalchemy import text
from common.utils.dataBase.interface.db_base_interface import DBBaseInterface

class DBSqliteBase(DBBaseInterface):
    """
    SQLite数据库基础操作类，继承自DBBaseInterface接口
    """
    def __init__(self, path: str):
        """
        初始化SQLite数据库连接
        
        参数:
            path: SQLite数据库文件路径
        """
        type = "sqlite+aiosqlite"
        self.url: str = f"{type}:///{path}"

    def connect(self):
        """
        连接到数据库并创建会话工厂
        """
        self.engine = create_async_engine(self.url, echo=True)
        self.sessionFactory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    def disconnect(self):
        """
        断开数据库连接
        """
        print("sqlite disconnect")

    async def get_session(self):
        """
        获取一个异步数据库会话
        
        返回:
            一个异步数据库会话生成器
        """
        async with self.sessionFactory() as session:
            yield session

    async def create_all(self, models: list) -> None:
        """
        创建所有模型对应的数据库表
        
        参数:
            models: 包含SQLModel类的列表
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(lambda sync_conn: [model.metadata.create_all(sync_conn) for model in models])

    async def execute(self, sql: str, params: dict | None = None):
        """
        执行原生SQL语句
        
        参数:
            sql: SQL语句，可以使用:param形式参数
            params: 参数字典(可选)
            
        返回:
            对于SELECT语句返回结果列表，其他操作返回影响行数
        """
        async with self.sessionFactory() as session:
            result = await session.execute(text(sql), params or {})
            await session.commit()
            
            if sql.strip().upper().startswith("SELECT"):
                return [dict(row._mapping) for row in result]
            return result.rowcount