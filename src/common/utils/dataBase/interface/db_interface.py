# baselib
from abc import ABC, abstractmethod


# 数据接口类  TODO 考虑合并
class DBInterface(ABC):
    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    def connect(self):
        """ 建立数据库连接"""
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError
    
    
#     数据库基类方法需要哪些，作为图数据库向量数据库等多种数据库的基类
# 数据库基类方法设计
# 作为图数据库、向量数据库等多种数据库的基类，应该包含以下核心方法：

# 连接管理
# connect(config: dict) -> bool: 建立数据库连接
# disconnect() -> bool: 关闭数据库连接
# is_connected() -> bool: 检查连接状态
# reconnect() -> bool: 重新连接数据库
# 基本CRUD操作
# create(collection: str, data: dict/object) -> str/object: 创建记录
# read(collection: str, query: dict, options: dict=None) -> list: 读取记录
# update(collection: str, query: dict, update_data: dict, options: dict=None) -> int: 更新记录
# delete(collection: str, query: dict, options: dict=None) -> int: 删除记录
# count(collection: str, query: dict=None) -> int: 统计记录数
# 事务管理
# begin_transaction() -> bool: 开始事务
# commit() -> bool: 提交事务
# rollback() -> bool: 回滚事务
# 集合/表管理
# create_collection(name: str, schema: dict=None) -> bool: 创建集合/表
# drop_collection(name: str) -> bool: 删除集合/表
# list_collections() -> list: 列出所有集合/表
# collection_exists(name: str) -> bool: 检查集合是否存在
# 索引管理
# create_index(collection: str, field: str, options: dict=None) -> bool: 创建索引
# drop_index(collection: str, index_name: str) -> bool: 删除索引
# list_indexes(collection: str) -> list: 列出索引
# 查询功能
# find(collection: str, query: dict, options: dict=None) -> cursor/iterator: 查询记录
# find_one(collection: str, query: dict, options: dict=None) -> dict/object: 查询单条记录
# aggregate(collection: str, pipeline: list) -> cursor/iterator: 聚合查询
# 特定于图数据库的方法
# create_node(label: str, properties: dict) -> str/object: 创建节点
# create_relationship(start_node: str/object, end_node: str/object, type: str, properties: dict) -> str/object: 创建关系
# traverse(start_node: str/object, traversal_spec: dict) -> list: 图遍历
# shortest_path(start_node: str/object, end_node: str/object, options: dict=None) -> list: 最短路径查询
# 特定于向量数据库的方法
# vector_search(collection: str, vector: list, options: dict) -> list: 向量相似度搜索
# batch_vector_search(collection: str, vectors: list, options: dict) -> list: 批量向量搜索
# create_vector_index(collection: str, field: str, index_type: str, options: dict) -> bool: 创建向量索引
# 管理方法
# execute_command(command: str/object) -> any: 执行原生命令
# get_stats() -> dict: 获取数据库统计信息
# backup(destination: str) -> bool: 备份数据库
# restore(source: str) -> bool: 恢复数据库
# 实用方法
# ping() -> bool: 检查数据库是否响应
# get_version() -> str: 获取数据库版本
# get_features() -> dict: 获取数据库支持的功能
# 这个基类设计提供了足够的抽象来支持多种数据库类型，同时允许特定数据库实现根据需要覆盖或扩展这些方法。