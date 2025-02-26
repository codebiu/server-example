from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

# self
from config.db import Data, DataNoCommit
from module_main.do.dict import Dict, DictCreate, DictPublic, DictUpdate
from common.utils.dataBase.DBEX import DBExtention


class DictDao:
    """dict"""


DBExtention.dao_init(DictDao, Dict, DictCreate, DictUpdate)
