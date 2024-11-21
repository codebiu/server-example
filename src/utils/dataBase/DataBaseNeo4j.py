from neo4j import AsyncGraphDatabase
from utils.dataBase.DataBaseInterface import DataBaseInterface


class DataBaseNeo4j(DataBaseInterface):
    url: str = None
    pwd: str = None
    user: str = None
    sessionLocal = None

    def __init__(self, user: str, pwd: str, host: str, port: int):
        self.url = f"neo4j://{host}:{port}"
        self.user = user
        self.pwd = pwd

    async def connect(self):
        self.driver = AsyncGraphDatabase.driver(self.url, auth=(self.user, self.pwd))
        self.sessionLocal = self.driver.session

    async def cypher_query(self, query: str, params: dict = None):
        async with self.sessionLocal() as session:
            result = await session.run(query, params)
            return result

    async def disconnect(self):
        await self.driver.close()
