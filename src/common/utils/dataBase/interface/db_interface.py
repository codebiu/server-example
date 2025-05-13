from common.utils.dataBase.interface.db_base_interface import DBBaseInterface
from common.utils.dataBase.interface.db_graph_interface import DBGraphInterface
from common.utils.dataBase.interface.db_relational_interface import DBRelationInterface
from common.utils.dataBase.interface.db_vector_interface import DBVectorInterface


class DBInterface(
    DBBaseInterface, DBRelationInterface, DBGraphInterface, DBVectorInterface
):
    """综合数据库接口"""

    pass
