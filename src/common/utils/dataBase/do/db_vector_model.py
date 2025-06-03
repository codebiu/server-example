from sqlmodel import SQLModel, Field, Column, text
from utils.db.do.vector import VECTOR as Vector
# class Vector(TypeDecorator):


class VectorMixin(SQLModel):
    """向量混合类（通过类属性动态设置维度）"""
    embedding: list[float] | None = Field(
        default=None,
        sa_column=Column(Vector()),  # 默认1024维
        description="向量嵌入表示",
    )


class Document(VectorMixin, table=True):
    __table_args__ = {"schema": "public"}
    id:str = Field(default=None, primary_key=True)
    project_id:str= Field(default=None, primary_key=True)
    content: str = Field()

    # 动态覆盖默认维度
    _VECTOR_DIM:int = 1024
    embedding: list[float] | None = Field(sa_column=Column(Vector(dim=_VECTOR_DIM)))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.embedding and len(self.embedding) != self._VECTOR_DIM:
            raise ValueError(f"向量维度必须为{self._VECTOR_DIM}")


class DocumentSelect(VectorMixin):
    __table_args__ = {"schema": "public"}
    id:str = Field(default=None, primary_key=True)
    content:str = Field()
    # 相似度
    similarity:float = Field(default=None)


# #
# -- 创建 documents 表
# CREATE TABLE public.documents (
#     id SERIAL PRIMARY KEY,
#     project_id INTEGER,
#     content TEXT,
#     embedding vector(1024)  -- 关键：使用 pgvector 类型
# );


if __name__ == "__main__":
    from utils.db.do.db_config import PostgresConfig
    from utils.db.impl.db_postgre_base import DBPostgreBase
    # 配置
    from config.index import conf
    db_config = conf["database.postgresql"]
    postgresConfig: PostgresConfig = PostgresConfig(**db_config)
    async def main():
        db_posgre = DBPostgreBase(postgresConfig)
        db_posgre.connect()
        async with db_posgre.engine.begin() as conn:
            # 确保pgvector扩展已安装
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            await conn.run_sync(SQLModel.metadata.create_all)
    import asyncio
    asyncio.run(main())