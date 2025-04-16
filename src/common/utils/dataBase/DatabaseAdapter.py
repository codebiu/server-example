class DatabaseMode(Enum):
    # ??? 还是用 sqlitegraph
    # 还有其他扩展?
    SQLITE_KUZU = "sqlite_sqlvec_kuzu"
    POSTGRES_AGE = "postgres_vector_age"


class DatabaseAdapter:
    """统一数据库适配器，使用组合模式"""

    def __init__(
        self,
        mode: DatabaseMode,
        relational_url: str,
        db_graph_path: str = None,
        db_graph_name: str = None,
    ):
        self.mode = mode
        

        # 根据模式组合不同的图数据库组件
        self.db_graph = None
        if mode == DatabaseMode.SQLITE_KUZU:
            self.db_relational = RelationalDatabase(relational_url)
            self.db_graph = KuzuGraphDatabase(db_graph_path)
            self.vector = VectorDatabase(db_graph_path)
        elif mode == DatabaseMode.POSTGRES_AGE:
            if not db_graph_name:
                raise ValueError("db_graph_name is required for PostgreSQL+AGE mode")
            self.db_graph = AgeGraphDatabase(self.db_relational, db_graph_name)

    def get_relational_session(self) -> Session:
        """获取关系型数据库会话"""
        return self.db_relational.get_session()

    def execute_graph_query(self, query: str, parameters: Optional[Dict] = None) -> Any:
        """执行图查询"""
        if not self.db_graph:
            raise NotImplementedError("Graph queries not supported in current mode")
        return self.db_graph.execute_query(query, parameters)

    def create_all(self, models: List[SQLModel]):
        """创建所有表和图模式"""
        self.db_relational.create_tables(models)
        if self.db_graph:
            self.db_graph.create_schema(models)

    def close(self):
        """关闭所有数据库连接"""
        self.db_relational.close()
        if self.db_graph:
            self.db_graph.close()
