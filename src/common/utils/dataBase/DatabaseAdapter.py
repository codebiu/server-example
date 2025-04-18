class DatabaseMode(Enum):
    # 嵌入式数据库
    EMBEDDED = "sqlite_sqlvec_kuzu"
    # postgres
    POSTGRES = "postgres_pgvector_apacheage"


class DatabaseAdapter:
    """统一异步数据库适配器，使用组合模式"""

    def __init__(

    ):
        """初始化数据库适配器"""
        
    def session_rel(self) -> AsyncSession:
        """获取关系型数据库会话"""
        
    # 获取有哪些图
    def get_graphs(self) -> List[str]:
        """获取所有图"""
        return self.db_graph.get_graphs()

    def close(self):
        """关闭所有数据库连接"""

