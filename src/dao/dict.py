from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

# self
from config.db import Data, DataNoCommit
from do.dict import Dict, DictCreate, DictPublic, DictUpdate
from utils.dataBase.DBEX import DBExtention


class DictDao:
    """dict"""


DBExtention.dao_init(DictDao, Dict, DictCreate, DictUpdate)
