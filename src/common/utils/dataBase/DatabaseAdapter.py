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
        graph_db_path: str = None,
        graph_db_name: str = None,
    ):
        self.mode = mode
        self.relational_db = RelationalDatabase(relational_url)

        # 根据模式组合不同的图数据库组件
        self.graph_db = None
        if mode == DatabaseMode.SQLITE_KUZU:
            if not graph_db_path:
                raise ValueError("graph_db_path is required for SQLite+Kuzu mode")
            self.graph_db = KuzuGraphDatabase(graph_db_path)
        elif mode == DatabaseMode.POSTGRES_AGE:
            if not graph_db_name:
                raise ValueError("graph_db_name is required for PostgreSQL+AGE mode")
            self.graph_db = AgeGraphDatabase(self.relational_db, graph_db_name)

    def get_relational_session(self) -> Session:
        """获取关系型数据库会话"""
        return self.relational_db.get_session()

    def execute_graph_query(self, query: str, parameters: Optional[Dict] = None) -> Any:
        """执行图查询"""
        if not self.graph_db:
            raise NotImplementedError("Graph queries not supported in current mode")
        return self.graph_db.execute_query(query, parameters)

    def create_all(self, models: List[SQLModel]):
        """创建所有表和图模式"""
        self.relational_db.create_tables(models)
        if self.graph_db:
            self.graph_db.create_schema(models)

    def close(self):
        """关闭所有数据库连接"""
        self.relational_db.close()
        if self.graph_db:
            self.graph_db.close()
