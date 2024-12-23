
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from utils.dataBase.DataBaseInterface import DataBaseInterface


class DataBasePostgre(DataBaseInterface):
    url: str = None
    pwd: str = None
    host: str = None
    port: int = None
    engine: create_async_engine = None
    sessionLocal: sessionmaker = None

    def __init__(self, path: str, user: str, pwd: str, host: str, port: int):
        type = "postgresql+asyncpg"
        # postgresql+asyncpg://hero:heroPass123@0.0.0.0:5432/heroes_db
        self.url = f"{type}://{user}:{pwd}@{host}:{port}/{path}"
        # todo: mysql
        #  "mysql+pymysql://user:password@host:port/database"

    def connect(self):
        # 控制台打印SQL
        self.engine = create_async_engine(self.url, echo=True)
        self.sessionLocal = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    def disconnect(self):
        print("postgresql disconnect")