# lib
import json
import sys, pathlib

[sys.path.append(str(pathlib.Path(__file__).resolve().parents[i])) for i in range(3)]
import time

# from common.utils.dataBase.DataBaseNeo4j import GraphTraversal
from common.utils.code.ast_python import AstPython
from common.utils.rag.graphRAG.prompt import AnalysisPrompt
from common.utils.media.openai.OpenAIClient import OpenAIClient

# 文件遍历
from common.utils.file.directory_tree import DirectoryTree


class GraphRAG:
    def __init__(self, project_path, project_name):
        self.project = project_path
        self.project_name = project_name
        self.chunker = AstPython()
        self._get_cypher()

    def _get_db(self, db):
        self.db = db
        self.db.connect()

    def _get_ai(self, embedding, invoke):
        self.embedding = embedding
        self.invoke = invoke

    def _get_cypher(self):
        self.cypterObj = {
            "query_create_file": f"""
                    CREATE (f:File {{ 
                        name: $label, 
                        path: $path, 
                        size: $size
                        }})
                    """,
            "query_create_folder": f"""
                                CREATE (f:Folder {{ 
                                    name: $label, 
                                    path: $path, 
                                    size: $size
                                    }})
                                """,
            "relation_folder_folder": f"""
                    MERGE (p:Folder {{name: $fp.label, path: $fp.path, size: $fp.size}})
                    MERGE (s:Folder {{name: $fs.label, path: $fs.path, size: $fs.size}})
                    CREATE (s)-[:in]->(p)
                    """,
            "relation_folder_file": f"""
                    MERGE (p:Folder {{name: $fp.label, path: $fp.path, size: $fp.size}})
                    CREATE (s:File {{name: $fs.label, path: $fs.path, size: $fs.size}})
                    CREATE (s)-[:in]->(p)
                    """,
            # 代码注释
            "relation_file_class": f"""
                    MERGE (p:File {{name: $label, path: $path, size: $size}})
                    CREATE (s:Class {{name: $name, byte_range: $byte_range, argument_list: $argument_list,class_string: $class_string,assignment: $assignment}})
                    CREATE (s)-[:belong]->(p)
            """,
            "relation_class_function": f"""
                    MERGE (p:Class {{name: $c.name, byte_range: $c.byte_range, argument_list: $c.argument_list}})
                    CREATE (s:Function {{name: $f.name, byte_range: $f.byte_range, code: $f.code, call: $f.call,
                    return_type: $f.return_type,size: $f.size, parameters: $f.parameters}})
                    CREATE (s)-[:belong]->(p)
            """,
            "relation_file_function": f"""
                    MERGE (p:File {{name: $fp.label, path: $fp.path, size: $fp.size}})
                    CREATE (s:Function {{name: $f.name, byte_range: $f.byte_range, code: $f.code, call: $f.call,
                    return_type: $f.return_type,size: $f.size, parameters: $f.parameters}})
                    CREATE (s)-[:belong]->(p)
            """,
            "file_import_other": f"""
                    MATCH (f:File {{path: $f}}) set f.import =$i,f.other =$o
            """,
            # "insert_call_file": f"""
            #         MERGE (p:File {{name: $label, path: $path, size: $size}})
            #         CREATE (s:Class {{name: $name, byte_range: $byte_range, argument_list: $argument_list}})
            #         CREATE (s)-[:belong]->(p)
            # """,
            "get_node_by_path": f"""
                    MATCH (n) where n.path = $path RETURN n as obj,id(n) as id, labels(n) as labels""",
            # 获取指向当前节点的子节点
            "get_node_child_by_id": f""" 
                    MATCH (n)-[]->(m) where id(m)=$id RETURN DISTINCT n as obj,id(n) as id, labels(n) as labels""",
            "add_describe_embedding_by_id": f"""
                    MATCH (n) where id(n)=$id set n.describe =$describe,n.embedding =$embedding
            """,
        }

    def _clear(self):
        self.db.cypher_query("MATCH (n) DETACH DELETE n")

    def _file_tree(self):
        self.directory_tree = DirectoryTree.build_directory_tree_root(self.project)

    def _graph_file(self):
        # 考虑文件迁移问题?
        start_time = time.time()
        self.num = {
            "folder": 0,
            "file": 0,
            "class": 0,
            "function": 0,
        }

        self._graph_tree_all(self.directory_tree)

        print("创建：", self.num)
        print("创建关系：", time.time() - start_time)

        # 解释节点(分层)

        # 聚合虚拟节点

    async def describe_all(self):
        # 将结果转换为字典列表
        path = "D:\\test\\ocrweb_multi_fastapi"
        # path = "D:\\test\\fastapi\\dependencies"
        records = self.db.match_query(
            self.cypterObj["get_node_by_path"],
            {"path": path},
        )
        #
        describe_all = await self.describe_node(records[0])

    async def describe_node(self, node_root):
        """从根节点广度处理每一层数据describe向上汇总"""
        obj = node_root["obj"]
        label = node_root["labels"][0]
        id = node_root["id"]
        # 只分析没有描述的节点
        # if "describe" not in obj:
        if True:
            # 获取子节点
            childs = self.db.match_query(
                self.cypterObj["get_node_child_by_id"],
                {"id": id},
            )
            describes = {}
            # 本体描述
            # describes["当前节点类别是:"] = label
            # describes["当前节点部分信息:"] = obj
            child_describes = None
            if len(childs) > 0:
                # 有子节点汇总信息
                tasks = [self.describe_node(node_child) for node_child in childs]
                child_describes = await asyncio.gather(*tasks)
                # describes["子节点信息汇总:"] = child_describes
                # 根据描述汇总
            # ai总结 子节点和本身
            # describes_json = json.dumps(describes, ensure_ascii=False)
            messages = []
            messages.append(AnalysisPrompt.get_prompt_system("python"))
            # 根据语言和节点类型分析获取prompt
            if label == "Function":
                messages.append(AnalysisPrompt.get_prompt_user_function("python", obj))
            elif label == "Class":
                messages.append(
                    AnalysisPrompt.get_prompt_user_class(obj, child_describes)
                )
            elif label == "File":
                # file_path = obj["path"]
                messages.append(
                    AnalysisPrompt.get_prompt_user_file(obj, child_describes)
                )
            elif label == "Folder":
                messages.append(
                    AnalysisPrompt.get_prompt_user_folder(obj, child_describes)
                )
            print(f'Task {str(id)} 开始解析 started at {time.strftime("%X")}')
            invoke_result = await self.invoke(messages)
            invoke_result = invoke_result["content"]
            obj["describe"] = invoke_result
            # 向量化
            if label == "Function":
                if obj["code"]:
                    invoke_result = invoke_result + "函数代码:" + obj["code"]
            embedding_result = await self.embedding(invoke_result)
            embedding_result = embedding_result
            # 图内插入节点信息
            self.db.match_query(
                self.cypterObj["add_describe_embedding_by_id"],
                {"id": id, "embedding": embedding_result, "describe": invoke_result},
            )
            print(f'Task {invoke_result} finished at {time.strftime("%X")}')
        # 返回节点描述
        return obj["describe"]

    def _graph_tree_all(self, node: dict, parent_node=None):
        """迭代创建节点插入图"""
        if "children" in node:
            node_folder = node
            # Folder
            self.db.cypher_query(self.cypterObj["query_create_folder"], node_folder)
            # 关联父子文件夹
            if parent_node is not None:
                self.db.cypher_query(
                    self.cypterObj["relation_folder_folder"],
                    {
                        "fp": parent_node,
                        "fs": node_folder,
                    },
                )
            for child in node_folder["children"]:
                self._graph_tree_all(child, node_folder)
            self.num["folder"] += 1
        else:
            node_file = node
            if not node['label'].endswith('.py'):
                return
            # 文件处理
            self.db.cypher_query(
                self.cypterObj["relation_folder_file"],
                {
                    "fp": parent_node,
                    "fs": node_file,
                },
            )
            # if(node_file['label'] =='models.py'):
            #     a =1
            # ast
            chunk = self.astCode_neo(node_file)
            if chunk is not None:
                # class解析
                for node_class in chunk["class"]:
                    self.num["class"] += 1
                    self.db.cypher_query(
                        self.cypterObj["relation_file_class"],
                        node_file | node_class,
                    )
                    # class 子函数
                    for node_function in node_class["function"]:
                        self.num["function"] += 1
                        self.db.cypher_query(
                            self.cypterObj["relation_class_function"],
                            {
                                "f": node_function,
                                "c": node_class,
                            },
                        )
                # function解析
                for node_function in chunk["function"]:
                    self.num["function"] += 1
                    self.db.cypher_query(
                        self.cypterObj["relation_file_function"],
                        {
                            "fp": node_file,
                            "f": node_function,
                        },
                    )
                # import解析
                self.db.cypher_query(
                    self.cypterObj["file_import_other"],
                    {
                        "f": node_file["path"],
                        "i": chunk["import"],
                        "o": chunk["other"],
                    },
                )

                self.num["file"] += 1
                print("解析完成...    ", node_file["path"])

    def astCode_neo(self, node_file):
        file_path = node_file["path"]
        if file_path.endswith(".py"):
            # 读取python文件到字符串
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
                new_chunk = self.chunker.chunk(text)
                return new_chunk

    async def create(self):
        start_time = time.time()
        self._clear()
        print("重置数据库", time.time() - start_time)
        self._file_tree()
        self._graph_file()
        await self.describe_all()



if __name__ == "__main__":
    # 引入路径
    import sys, pathlib
    [
        sys.path.append(str(pathlib.Path(__file__).resolve().parents[i]))
        for i in range(4)
    ]
    # self
    from common.utils.dataBase.DataBaseNeo4j import DataBaseNeo4j
    from config.index import conf

    # lib
    import asyncio

    async def main():
        start_time = time.time()
        print("db连接", time.time() - start_time)
        start_time = time.time()
        project = r"D:\test\ocrweb_multi_fastapi"
        project_name = "ocrweb_multi_fastapi"
        # 获取图数据库
        neo4j = conf["database"]["neo4j"]
        host = neo4j["host"]
        port = neo4j["port"]
        user = neo4j["user"]
        password = neo4j["password"]
        database = neo4j["database"]
        db = DataBaseNeo4j(user, password, host, port, database)

        # 获取ai_api
        openai_set = conf["ai"]["openai"]
        # openai_set = conf["ai"]["aihubmix"]
        client = OpenAIClient(
            api_key=openai_set["api_key"],
            chat_url=openai_set["chat_url"],
            chat_model=openai_set["chat_model"],
            embedding_url=openai_set["embedding_url"],
            embedding_model=openai_set["embedding_model"],
        )

        # 构建图
        graphRAG = GraphRAG(project, project_name)
        graphRAG._get_db(db)
        graphRAG._get_ai(client.embedding, client.invoke)
        await graphRAG.create()

    # 运行主函数
    asyncio.run(main())
