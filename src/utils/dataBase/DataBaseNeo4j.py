import time    
from neo4j import GraphDatabase
from utils.dataBase.DataBaseInterface import DataBaseInterface


class DataBaseNeo4j(DataBaseInterface):
    url: str = None
    pwd: str = None
    user: str = None
    driver = None

    def __init__(self, user: str, pwd: str, host: str, port: int,path: str ="neo4j" ):
        self.url = f"neo4j://{host}:{port}"
        self.user = user
        self.pwd = pwd
        self.path = path  # 指定默认数据库
        

    def connect(self):
        # 使用同步的驱动程序
        self.driver = GraphDatabase.driver(self.url, auth=(self.user, self.pwd), database=self.path,max_connection_pool_size=100)

    def cypher_query(self, query: str, params: dict = None):
        with self.driver.session() as session:
            # 执行Cypher查询并获取结果
            result = session.run(query, params)
            return result
        
    def cypher_query_batch(self, query: str, params_list: list = None):
        results = []
        with self.driver.session() as session:
            if params_list is not None:
                for param in params_list:
                    # print(f'Task {param["path"]} start at {time.strftime("%X")}')  
                    # 执行Cypher查询并获取结果
                    result = session.run(query, param)
                    results.append(result)
            else:
                result = session.run(query)
                results.append(result)
                # print(f'Task {param["path"]} finished at {time.strftime("%X")}')  
        return results
    
    def cypher_query_batchs(self, query_objs: list = None):
        results = []
        with self.driver.session() as session:
            for query_obj in query_objs:
                query = query_obj['query']
                if query_obj.get('params') is not None:
                    params_list = query_obj['params']
                    for param in params_list:
                        # print(f'Task {param["path"]} start at {time.strftime("%X")}')  
                        # 执行Cypher查询并获取结果
                        result = session.run(query, param)
                        results.append(result)
                else:
                    params_list = None
                    result = session.run(query)
                    results.append(result)
                    # print(f'Task {param["path"]} finished at {time.strftime("%X")}')  
        return results

    def disconnect(self):
        if self.driver:
            self.driver.close()