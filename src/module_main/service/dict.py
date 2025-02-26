# self
from module_main.do.dict import Dict,DictCreate,DictUpdate
from module_main.dao.dict import DictDao
from common.utils.dataBase.DBEX import DBExtention
# lib


class DictService:
    """dict"""

DBExtention.service_init(DictService,DictDao,Dict,DictCreate,DictUpdate)