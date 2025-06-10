# 项目模块导入
from common.utils.db.do.db_config import DBEX,DBConfig
from config.log import logger
from config.index import conf

state_db = conf["state.db"]
if not state_db:
    logger.info("未配置db")
db_configs = conf[f"db.{state_db}"]

# 数据库对象
db_rel = None
db_vec = None
db_graph =  None
db_es =  None
try:
    # config
    # 关系数据库 基础库
    rel = db_configs["rel"]
    if not rel:
        raise Exception("未配置关系数据库(基础数据库)")
    rel_config: DBConfig = DBEX.get_config(rel["type"], rel)
    # vec
    # graph
    # es
    
    
except Exception as e:
    logger.error(f"数据库初始化失败: {e}")


if  __name__ == "__main__":
    pass


