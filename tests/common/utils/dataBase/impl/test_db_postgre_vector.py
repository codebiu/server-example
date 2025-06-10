# 测试文件：D:\a0_wx\codebiu\server-example\src\common\utils\dataBase\impl\db_postgre_vector.py
import pytest

from common.utils.db.do.db_config import PostgresConfig
from common.utils.db.do.db_vector_model import Document, DocumentSelect
from common.utils.db.impl.db_postgre_base import DBPostgreBase
from common.utils.db.impl.db_postgre_vector import DataBasePostgreVector
# 在此添加测试用例
import numpy as np
# 配置
from config.index import conf
from sqlmodel import select

db_config = conf["database.postgresql"]
postgresConfig: PostgresConfig = PostgresConfig(**db_config)

async def content_embedding_test_data(session, pid="proj_1", count=6, dim=1024):
    """生成测试数据"""

    # 生成随机向量（1024维）
    def random_vector():
        return [float(x) for x in np.random.rand(dim).tolist()]

    target = {"content": f"目标文档", "embedding": [0.1] * dim, "pid": pid}
    documents = [target]
    for i in range(count):
        documents.append(
            {"content": f"文档内容 {i}", "embedding": random_vector(), "pid": pid}
        )
    return documents, target

async def insert_test_data(session):
    """插入测试数据"""
    documents_0, target = await content_embedding_test_data(
        session, pid="proj_0", count=6
    )
    documents_1, target = await content_embedding_test_data(
        session, pid="proj_1", count=6
    )
    documents = documents_0 + documents_1
    documents_table_add = []
    for document in documents:
        documents_table_add.append(Document(**document))
    session.add_all(documents_table_add)
    await session.commit()
    print("已插入测试数据")



async def main():
    db_posgre = DBPostgreBase(postgresConfig)
    db_posgre.connect()
    db_posgre_vector = DataBasePostgreVector()
    # async with db_posgre.engine.begin() as conn:
    #     # 确保pgvector扩展已安装
    #     await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    #     await conn.run_sync(SQLModel.metadata.create_all)
    # 插入数据和执行搜索
    async with db_posgre.session_factory() as session:
        # await insert_test_data(session)
        document_selects = await db_posgre_vector.cosine(session, Document,DocumentSelect, [0.1] * 1024, "proj_0",3)
        for doc in document_selects:
            print(
                f"ID: {doc.id:8} | 内容: {doc.content:10} | 相似度: {doc.similarity:.4f}"
            )

    await db_posgre.engine.dispose()

import asyncio

asyncio.run(main())
