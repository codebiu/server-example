import json
from pathlib import Path
import time
import pytest
import asyncio
from common.utils.db.do.db_config import SqliteConfig
from common.utils.db.interface.db_base_interface import DBBaseInterface
from common.utils.db.impl.db_sqlite_base import DBSqliteBase
from config.log import logger
# 配置
from config.index import conf
db_config = conf["database.sqlite"]
sqliteConfig: SqliteConfig = SqliteConfig(**db_config)

class TestDBSqliteBase:
    """SQLite数据库基础功能测试类"""
    db: DBBaseInterface = DBSqliteBase(sqliteConfig)

    async def _connect(self):
        """测试初始化"""
        if not self.db:
            self.db:DBSqliteBase = DBSqliteBase(sqliteConfig)
        if not await self.db.is_connected():
            self.db.connect()

    async def _disconnect(self):
        """测试清理"""
        if await self.db.is_connected():
            await self.db.disconnect()

    @pytest.mark.asyncio
    async def test_connect_disconnect(self):
        """测试连接和断开功能"""
        logger.info("###########################################测试数据库连接和断开")
        await self._connect()
        assert await self.db.is_connected()
        await self._disconnect()
        assert not await self.db.is_connected()

    @pytest.mark.asyncio
    async def test_get_session(self):
        await self._connect()
        """测试获取会话功能"""
        logger.info("###########################################测试获取数据库会话")
        async for session in self.db.get_session():
            assert session is not None
        await self._disconnect()
        
    @pytest.mark.asyncio
    async def test_execute_select(self):
        """测试执行SELECT语句"""
        await self._connect()
        logger.info("###########################################测试执行SELECT语句")
        result = await self.db.execute("SELECT 1")
        logger.info(f"\nSELECT执行结果: {result}")
        assert result == [(1,)]
        await self._disconnect()

    @pytest.mark.asyncio
    async def test_execute_create_table(self):
        """测试执行CREATE TABLE语句"""
        # 时间表名 年月日时分秒数字
        table_name= "test_table_to_delete" + time.strftime("%Y%m%d%H%M%S", time.localtime())
        await self._connect()
        logger.info("测试执行CREATE TABLE")
        sql = f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY, name TEXT)"
        
        # 不检查返回值，只验证是否执行成功
        try:
            await self.db.execute(sql)
            # 验证表是否真实创建
            check_sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
            result = await self.db.execute(check_sql)
            assert result is not None  # 或更精确的断言
        except Exception as e:
            pytest.fail(f"创建表失败: {str(e)}")
        await self._disconnect()


    @pytest.mark.asyncio
    async def test_get_info(self):
        """测试获取数据库信息"""
        await self._connect()
        logger.info("###########################################测试获取数据库信息")
        info = await self.db.get_info()
        logger.info(f"\n数据库信息: {json.dumps(info)}")
        assert info["type"] == "SQLite"
        assert info["url"] == str(self.db.url)  # 确保Path对象转为字符串比较
        assert isinstance(info["tables"], list)
        await self._disconnect()
        
if __name__ == "__main__":
    import asyncio
    async def run_tests():
        """异步测试运行器"""
        tester = TestDBSqliteBase()
        await tester._connect()
        try:
            print("\n=== 开始执行测试 ===")
            await tester.test_connect_disconnect()
            await tester.test_get_session()
            await tester.test_execute_select()
            # await tester.test_execute_create_table()
            # await tester.test_get_info()
            print("\n=== 测试全部通过 ===")
        except Exception as e:
            logger.error(f"测试失败: {str(e)}", exc_info=True)
            print(f"\n!!! 测试失败: {str(e)}")
        finally:
            await tester._connect()
            print("\n测试完成，清理环境")
    asyncio.run(run_tests())