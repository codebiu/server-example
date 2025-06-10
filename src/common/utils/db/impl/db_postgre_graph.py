from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from common.utils.db.interface.db_base_interface import DBBaseInterface


class DataBasePostgreBase(DBBaseInterface):
  

    def __init__(self, user: str, pwd: str, host: str, port: int, database: str):
        type = "postgresql+asyncpg"
        # postgresql+asyncpg://hero:heroPass123@0.0.0.0:5432/heroes_db
        self.url = f"{type}://{user}:{pwd}@{host}:{port}/{database}"
        self.engine: create_async_engine = None
        self.sessionFactory: sessionmaker = None

    def connect(self):
        # 控制台打印SQL
        self.engine = create_async_engine(
            self.url,
            echo=True,
            # 其余数据库设置
        )
        self.sessionFactory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    def disconnect(self):
        print("postgresql disconnect")
