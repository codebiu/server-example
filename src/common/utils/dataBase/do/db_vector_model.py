import uuid
from sqlmodel import SQLModel, Field, Column, text

# from utils.db.do.vector import VECTOR as Vector
from utils.db.do.vector_pg import VectorPG

# class Vector(TypeDecorator):
#     """动态维度的向量类型（不依赖pgvector包）"""

#     impl = "vector"
#     cache_ok = True

#     def __init__(self, dim=1024, **kwargs):
#         super().__init__(**kwargs)
#         self.dim = dim

#     @property
#     def python_type(self):
#         return list

#     def load_dialect_impl(self, dialect):
#         if dialect.name == 'postgresql':
#             return dialect.type_descriptor(f"vector({self.dim})")
#         else:
#             return dialect.type_descriptor(text("TEXT"))

#     def process_bind_param(self, value, dialect):
#         if value is None:
#             return None
#         return "[" + ",".join(map(str, value)) + "]"

#     def process_result_value(self, value, dialect):
#         if value is None:
#             return None
#         if isinstance(value, str):
#             return [float(x) for x in value.strip("[]").split(",")]
#         return value


class VectorMixin(SQLModel):
    """向量混合类（通过类属性动态设置维度）"""

    embedding: list[float] | None = Field(
        default=None,
        sa_column=Column(VectorPG()),  # 默认1024维
        description="向量嵌入表示",
    )


class DocumentBase(SQLModel):
    __table_args__ = {"schema": "public"}
    id: str = Field(default_factory=lambda: uuid.uuid4().hex, primary_key=True)
    content: str = Field()


class Document(VectorMixin, DocumentBase, table=True):
    pid: str = Field(default_factory=lambda: uuid.uuid4().hex)
    # 动态覆盖默认维度
    _VECTOR_DIM: int = 1024
    embedding: list[float] | None = Field(sa_column=Column(VectorPG(dim=_VECTOR_DIM)))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.embedding and len(self.embedding) != self._VECTOR_DIM:
            raise ValueError(f"向量维度必须为{self._VECTOR_DIM}")


class DocumentSelect(DocumentBase):
    similarity: float = Field(default=None)  # 相似度


# #
# -- 创建 documents 表
# CREATE TABLE public.documents (
#     id SERIAL PRIMARY KEY,
#     pid INTEGER,
#     content TEXT,
#     embedding vector(1024)  -- 关键：使用 pgvector 类型
# );


if __name__ == "__main__":
    import numpy as np
    from utils.db.do.db_config import PostgresConfig
    from utils.db.impl.db_postgre_base import DBPostgreBase
    from utils.db.impl.db_postgre_vector import DataBasePostgreVector
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
