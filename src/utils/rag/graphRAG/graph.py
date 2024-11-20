import kuzu

class Graph:
    def __init__(self,path="D:/test/kuzu_db"):
        # 初始化 Kùzu 图数据库
        self.path = path
        self.db = kuzu.Database(path)
        self.conn = kuzu.Connection(self.db)
        pass
    
    def refresh(self,path):
        # 清空path下Kùzu MATCH (n) DETACH DELETE n
        self.conn.execute("MATCH (n) DETACH DELETE n")
        
    def create(self):
        
        # 创建节点表
        self.conn.execute("""
        CREATE NODE TABLE Folder (
            path STRING,
            PRIMARY KEY (path)
        );
        """)

        self.conn.execute("""
        CREATE NODE TABLE File (
            path STRING,
            size INT64,
            PRIMARY KEY (path)
        );
        """)

        # 创建边表
        self.conn.execute("""
        CREATE EDGE TABLE Contains (
            FROM Folder TO Folder,
            PRIMARY KEY (FROM, TO)
        );
        """)

        self.conn.execute("""
        CREATE EDGE TABLE ContainsFile (
            FROM Folder TO File,
            PRIMARY KEY (FROM, TO)
        );
        """)