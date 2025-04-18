from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from common.utils.dataBase.interface.db_interface import DBInterface
from common.utils.dataBase.interface.db_relational_interface import DBRelationInterface


class DataBasePostgre(DBInterface,DBRelationInterface):
  

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
        
        
    # async def get_heroes_older_than(self, min_age: int):
    #     async with self.sessionFactory() as session:
    #         # 使用参数化查询防止 SQL 注入
    #         result = await session.execute(
    #             text("""
    #                 SELECT id, name, age 
    #                 FROM heroes 
    #                 WHERE age > :age_threshold 
    #                 ORDER BY age DESC
    #             """),
    #             {"age_threshold": min_age}
    #         )
    #         return result.mappings().all()  # 返回字典列表