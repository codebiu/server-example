from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
# 防止注入
from sqlalchemy import text
from common.utils.dataBase.interface.db_base_interface import DBBaseInterface

class DBSqliteBase(DBBaseInterface):
    """SQLite 数据库基础实现类 (Python 3.10+ 语法)
    
    特性：
    - 使用 pathlib 替代 os 处理路径
    - 使用 SQLAlchemy 异步引擎
    - 完全实现 DBBaseInterface 接口
    - 采用 Python 3.10+ 新语法
    """
    
    url: str | None = None
    engine = None
    session_factory = None

    def __init__(self, db_path: str | Path):
        """初始化 SQLite 数据库连接
        
        Args:
            db_path: 数据库文件路径，可以是字符串或 Path 对象
        """
        # 使用 pathlib 规范化路径
        db_path = Path(db_path) if isinstance(db_path, str) else db_path
        self.url = f"sqlite+aiosqlite:///{db_path.absolute()}"

    def connect(self):
        """建立数据库连接"""
        self.engine = create_async_engine(self.url, echo=True)
        self.session_factory = sessionmaker(
            self.engine, 
            expire_on_commit=False, 
            class_=AsyncSession
        )

    async def is_connected(self) -> bool:
        """检查连接状态"""
        return bool(self.engine and not await self.engine.disposed)

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

    async def get_info(self) -> dict:
        """获取数据库信息"""
        return {
            "type": "SQLite",
            "url": self.url,
            "connected": await self.is_connected(),
            "tables": await self._get_table_list()
        }

    async def get_session(self):
        """获取异步会话"""
        async with self.session_factory() as session:
            yield session

    async def create_all(self, models: list):
        """创建所有表结构"""
        async with self.engine.begin() as conn:
            await conn.run_sync(
                lambda sync_conn: [model.metadata.create_all(sync_conn) for model in models]
            )

    async def execute(self, sql: str, params: dict | None = None):
        """执行原生SQL
        
        Args:
            sql: SQL语句 (支持 :param 参数)
            params: 参数字典
            
        Returns:
            SELECT 返回结果列表，其他操作返回影响行数
        """
        async with self.session_factory() as session:
            result = await session.execute(text(sql), params or {})
            await session.commit()
            
            if sql.strip().upper().startswith("SELECT"):
                return [dict(row._mapping) for row in result]
            return result.rowcount

    async def _get_table_list(self) -> list[str]:
        """获取所有表名 (内部方法)"""
        if not await self.is_connected():
            return []
            
        sql = "SELECT name FROM sqlite_master WHERE type='table'"
        tables = await self.execute(sql)
        return [table["name"] for table in tables]