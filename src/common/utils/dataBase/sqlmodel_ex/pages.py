from typing import Generic, TypeVar, Optional, Union, List, Tuple, Any
from fastapi import Query
from sqlmodel import SQLModel, select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.selectable import Select

# 定义泛型类型
T = TypeVar("T")

class PageParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="页码"),
        size: int = Query(20, ge=1, le=100, description="每页数量"),
    ):
        self.page = page
        self.size = size

# class Page(SQLModel, Generic[T]):
#     items: list[T]
#     total: int
#     page: int
#     size: int
#     pages: int

#     @classmethod
#     def create(cls, items: list[T], total: int, params: PageParams):
#         pages = (total + params.size - 1) // params.size
#         return cls(
#             items=items,
#             total=total,
#             page=params.page,
#             size=params.size,
#             pages=pages,
#         )

# async def paginate(
#     session: AsyncSession,
#     model: type[SQLModel],
#     params: PageParams,
#     where: Optional[list] = None,
#     order_by: Optional[list] = None,
#     select_fields: Optional[Union[List[str], Tuple[Any, ...]]] = None,
# ) -> Page[SQLModel]:
#     """
#     支持部分字段查询的分页函数
    
#     Args:
#         session: 异步数据库会话
#         model: SQLModel模型类
#         params: 分页参数
#         where: 查询条件列表
#         order_by: 排序条件列表
#         select_fields: 要查询的字段列表，可以是字段名列表或SQLAlchemy列对象元组
#     """
#     # 计算总数
#     count_stmt = select(func.count()).select_from(model)
#     if where:
#         count_stmt = count_stmt.where(*where)
#     total = (await session.execute(count_stmt)).scalar_one()
    
#     # 构建查询语句
#     if select_fields is None:
#         # 查询所有字段
#         stmt = select(model)
#     else:
#         # 查询指定字段
#         if isinstance(select_fields[0], str):
#             # 如果是字段名列表，转换为模型属性
#             fields = [getattr(model, field) for field in select_fields]
#             stmt = select(*fields)
#         else:
#             # 如果是SQLAlchemy列对象，直接使用
#             stmt = select(*select_fields)
    
#     # 添加条件和排序
#     if where:
#         stmt = stmt.where(*where)
#     if order_by:
#         stmt = stmt.order_by(*order_by)
    
#     # 添加分页
#     stmt = stmt.offset((params.page - 1) * params.size).limit(params.size)
    
#     # 执行查询
#     result = await session.execute(stmt)
    
#     # 处理结果
#     if select_fields is None:
#         items = result.scalars().all()
#     else:
#         if isinstance(select_fields[0], str):
#             # 对于字段名列表，返回字典列表
#             items = [dict(zip(select_fields, row)) for row in result.all()]
#         else:
#             # 对于SQLAlchemy列对象，返回元组列表
#             items = result.all()
    
#     return Page.create(items, total, params)