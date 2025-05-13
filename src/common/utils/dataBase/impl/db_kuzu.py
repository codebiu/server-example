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
        

