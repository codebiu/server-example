import kuzu,polars

class DataBaseKuzu:
    def connect(self,path):
        try:
            # 初始化 Kùzu 图数据库
            self.path = path
            self.db = kuzu.Database(path)
            self.conn = kuzu.Connection(self.db)
            print("successfully connected to Kùzu graph database")
        except Exception as e:
            print(f"failed to connect to Kùzu graph database: {e}")
            
    def clear_all(self):
        self.drop_tables_all()
    
    def clear_data(self):
        '''清空数据'''
        self.conn.execute("MATCH (n) DETACH DELETE n")
        
    def drop_tables_all(self):
        '''清空标签和数据'''
        tables = self.list_tables()
        for table in tables:
            self.drop_table(table['name'])
        
    def list_tables(self):
        tables = self.conn.execute("CALL show_tables() RETURN *;").get_as_pl().to_dicts()
        return tables
    
    def drop_table(self,table_name):
        self.conn.execute(f"DROP TABLE  IF EXISTS {table_name}")


    def show_data_25(self):
        result =  self.conn.execute("MATCH (n) RETURN n LIMIT 25").get_as_pl()
        print(result)
        
    def create(self):
        
        # 创建节点表
        self.conn.execute("CREATE NODE TABLE Folder ( path STRING, PRIMARY KEY (path) )")

        self.conn.execute("CREATE NODE TABLE File ( path STRING, size INT64, PRIMARY KEY (path) );")

        self.conn.execute("CREATE REL TABLE Belong(FROM Folder TO Folder)")
        self.conn.execute("CREATE REL TABLE Belong(FROM File TO Folder)")
        
if __name__ == "__main__":

    # # 文件遍历
    # from utils.file.directory_tree import DirectoryTree
    # # directory_tree = DirectoryTree.build_directory_tree(r'D:\test\fastapi')
    # # # 将目录树转换为 JSON 格式
    # # json_tree = json.dumps(
    # #     directory_tree,
    # #     #默认输出ASCLL码，False可以输出中文。
    # #     # 带格式
    # #     indent=4,
    # #     ensure_ascii=False,
    # # )
    # # print(json_tree)
    
    # path_grapg_db ="D:/test/kuzu_db"
    # graph = KuzuGraph(path_grapg_db)
    # # graph.refresh()
    # # graph.clear_database()
    # # graph.create()
    # conn = graph.conn