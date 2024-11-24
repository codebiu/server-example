from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from utils.dataBase.DataBaseInterface import DataBaseInterface

class DataBaseSqlite(DataBaseInterface):
    url: str = None
    engine: create_async_engine = None
    sessionLocal: sessionmaker = None

    def __init__(self, path: str):
        # 打包跟随程序
        type = "sqlite+aiosqlite"
        self.url = f"{type}:///{path}"

    def connect(self):
        # 控制台打印SQL
        self.engine = create_async_engine(self.url, echo=True)
        self.sessionLocal = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    def disconnect(self):
        print("sqlite disconnect")
