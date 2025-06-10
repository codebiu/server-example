import time
from neo4j import AsyncGraphDatabase,GraphDatabase
from common.utils.db.DataBaseInterface import DataBaseInterface


class DataBaseNeo4jAsync(DataBaseInterface):
    url: str = None
    pwd: str = None
    user: str = None
    sessionFactory = None

    def __init__(self, user: str, pwd: str, host: str, port: int,path: str ="neo4j" ):
        self.url = f"neo4j://{host}:{port}"
        self.user = user
        self.pwd = pwd
        self.path = path  # 指定默认数据库
        
    async def connect(self):
        self.driver = AsyncGraphDatabase.driver(self.url, auth=(self.user, self.pwd), database=self.path,max_connection_pool_size=100)
        self.sessionFactory = self.driver.session

    async def cypher_query(self, query: str, params: dict = None):
        async with self.sessionFactory() as session:
            result = await session.run(query, params)
            return result
        

    async def disconnect(self):
        await self.driver.close()
 
    # def cypher_query(self, query: str, params: dict = None):
    #     with self.driver.session() as session:
    #         # 执行Cypher查询并获取结果
    #         result = session.run(query, params)
    #         return result
        
    # def cypher_query_batch(self, query: str, params_list: list = None):
    #     results = []
    #     with self.driver.session() as session:
    #         for param in params_list:
    #             print(f'Task {param["path"]} start at {time.strftime("%X")}')  
    #             # 执行Cypher查询并获取结果
    #             result = session.run(query, param)
    #             results.append(result)
    #             print(f'Task {param["path"]} finished at {time.strftime("%X")}')  
    #     return results
    
    # def cypher_query_batchs(self, query_objs: list = None):
    #     results = []
    #     with self.driver.session() as session:
    #         for query_obj in query_objs:
    #             params_list = query_obj['params']
    #             query = query_obj['query']
    #             for param in params_list:
    #                 print(f'Task {param["path"]} start at {time.strftime("%X")}')  
    #                 # 执行Cypher查询并获取结果
    #                 result = session.run(query, param)
    #                 results.append(result)
    #                 print(f'Task {param["path"]} finished at {time.strftime("%X")}')  
    #     return results
