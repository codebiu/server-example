from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import text
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, inspect, select
from common.utils.db.interface.db_base_interface import DBBaseInterface


class DataBasePostgreVector(DBBaseInterface):
    async def cosine(
        self,
        session: AsyncSession,
        model_in,
        model_out,
        search_vector,
        pid="proj_1",
        limit=3,
    ):
        query = (
            select(
                model_in.id,
                model_in.content,
                (1.0 - model_in.embedding.cosine(search_vector)).label("similarity"),
            )
            .where(model_in.pid == pid)
            .order_by(model_in.embedding.cosine(search_vector))
            .limit(limit)
        )
        results = await session.exec(query)
        # 结果转换为DocumentSelect对象
        document_selects = []
        for row in results:
            document_selects.append(model_out(**row._asdict()))
        return document_selects


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
