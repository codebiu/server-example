from sqlmodel import SQLModel, Field, Column
from sqlalchemy import TypeDecorator

class Vector(TypeDecorator):
    """动态维度的向量类型（不依赖pgvector包）"""
    impl = "vector"  # 基础类型名称

    def __init__(self, dim=1024, **kwargs):
        super().__init__(**kwargs)
        self.dim = dim

    @property
    def python_type(self):
        return list

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(f"vector({self.dim})")

class VectorMixin(SQLModel):
    """向量混合类（通过类属性动态设置维度）"""
    embedding = Field(
        default=None,
        sa_column=Column(Vector()),  # 默认1024维
        description="向量嵌入表示"
    )

class Document(VectorMixin, table=True):
    __table_args__ = {"schema": "public"}
    id = Field(default=None, primary_key=True)
    project_id = Field(default=None, primary_key=True)
    content:str = Field()
    
    # 动态覆盖默认维度
    VECTOR_DIM = 1024
    embedding = Field(
        sa_column=Column(Vector(dim=VECTOR_DIM))
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.embedding and len(self.embedding) != self.VECTOR_DIM:
            raise ValueError(f"向量维度必须为{self.VECTOR_DIM}")
class DocumentSelect(VectorMixin, table=True):
    __table_args__ = {"schema": "public"}
    id = Field(default=None, primary_key=True)
    content = Field()
    # 相似度
    similarity = Field(default=None)
        
# # 
# -- 创建 documents 表
# CREATE TABLE public.documents (
#     id SERIAL PRIMARY KEY,
#     project_id INTEGER,
#     content TEXT,
#     embedding vector(1024)  -- 关键：使用 pgvector 类型
# );