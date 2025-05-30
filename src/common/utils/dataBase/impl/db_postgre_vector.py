from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import text
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, inspect, select
from utils.db.interface.db_base_interface import DBBaseInterface


class DataBasePostgreVector(DBBaseInterface):
    def __init__(self, engine, sessionFactory):
        self.engine = engine
        self.sessionFactory = sessionFactory

    async def select_by_cosine(
        self,
        session,
        model,  # 接收 DocumentSelect 这类模型
        query_vector,
        filter_column=None,
        filter_value=None,
        top_n=5,
        vector_column="embedding",
        similarity_alias="similarity",
    ):
        """
        通用向量搜索，返回指定model类型的对象（需包含similarity字段）
        """
        # 获取原始表模型（如 Document）
        base_model = model.__bases__[0] if hasattr(model, "__bases__") else model

        # 验证模型是否包含similarity字段
        if not any(field.name == "similarity" for field in model.__fields__.values()):
            raise ValueError("返回模型必须包含 similarity 字段")

        # 构建查询字段（排除向量）
        select_fields = [
            getattr(base_model, col.name)
            for col in inspect(base_model).columns
            if col.name != vector_column
        ]

        # 添加过滤条件
        stmt = select(*select_fields)
        if filter_column is not None:
            stmt = stmt.where(filter_column == filter_value)

        # 添加相似度计算
        vec_str = ",".join(str(v) for v in query_vector)
        stmt = (
            stmt.add_columns(
                text(f"{vector_column} <=> ARRAY[{vec_str}]::vector").label(
                    similarity_alias
                )
            )
            .order_by(similarity_alias)
            .limit(top_n)
        )

        # 执行并映射结果
        result = await session.execute(stmt)
        return [
            model(**row._asdict())  # 自动匹配字段名
            for row in result
        ]


if __name__ == "__main__":
    # results = await vector_search(
    # session=session,
    # model=Document,
    # query_vector=[0.1]*1024,
    # filter_column=Document.project_id,
    # filter_value=1,
    # top_n=3
    # )
    pass
