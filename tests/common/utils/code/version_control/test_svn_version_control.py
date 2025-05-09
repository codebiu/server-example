import json
import pytest
from config.path import dir_test
from common.utils.code.version_control.svn_version_control import SVNVersionControl
from common.utils.file.dir_manager import DirManager
from config.log import logger, setup_logging

# 测试配置
TEST_SVN_URL = "https://A52230321050007/svn/test_svn_project1/"  # 本地SVN服务地址
TEST_LOCAL_PATH = dir_test / "svn_test_repo"
TEST_BRANCH = "HEAD"
TEST_USERNAME = "wx"  # SVN账号
TEST_PASSWORD = "123"  # SVN密码
TEST_FILE = "test_file.txt"  # 测试文件名
TEST_COMMIT_MSG = "自动化测试提交"  # 提交消息


class TestSVNVersionControl:
    """SVN版本控制完整测试"""

    @classmethod
    def setup_class(cls):
        """测试初始化"""
        cls.repo_path = TEST_LOCAL_PATH
        # 初始化SVN客户端
        cls.svn = SVNVersionControl(
            repo_path=TEST_LOCAL_PATH, username=TEST_USERNAME, password=TEST_PASSWORD
        )

    def test_checkout_repository(self):
        """测试首次检出仓库"""
        # 测试强制删除已有仓库
        if self.repo_path.exists():
            DirManager.remove_dir(self.repo_path)
        assert not self.repo_path.exists()
        # 首次检出
        result = self.svn.clone_or_checkout(repo_url=TEST_SVN_URL, revision=TEST_BRANCH)
        logger.info(
            "###########################################svn测试克隆/检出真实仓库"
        )
        logger.info("\nSVN检出操作结果:", result)  # 打印详细结果

        if result["status"] == "error":
            pytest.fail(f"SVN检出失败: {result['message']}")  # 明确显示错误原因

        assert result["status"] == "success"
        assert (self.repo_path / ".svn").exists()

    def test_get_changes_between_revisions(self):
        """测试获取两个版本之间的变更"""
        # 确保仓库已检出
        if not self.repo_path.exists():
            self.test_checkout_repository()
        # 获取版本1和版本2之间的变更
        result = self.svn.get_changes_between_revisions(1,12)
        logger.info(
            "###########################################svn测试获取两个版本之间的变更"
        )
        logger.info("\nSVN获取版本变更结果: %s", json.dumps(result))
        assert result["status"] == "success"
        # assert isinstance(result["changes"], list)
        # assert len(result["changes"]) > 0

    def test_update_repository(self):
        """测试更新仓库"""
        # 确保仓库已检出
        if not self.repo_path.exists():
            self.test_checkout_repository()

        # 执行更新操作
        result = self.svn.update()
        logger.info("###########################################svn测试更新仓库")
        logger.info("\nSVN更新操作结果: %s", json.dumps(result))

        # 验证更新结果
        assert result["status"] == "success"
        assert "old_version" in result
        assert "new_version" in result
        assert "changes" in result
        assert isinstance(result["changes"], list)

        # 验证版本号是否有效
        if result["old_version"] != result["new_version"]:
            assert len(result["changes"]) > 0
        else:
            assert len(result["changes"]) == 0

    def test_destroy_after_checkout(self):
        """测试删除仓库"""
        result = self.svn.destroy_repository()
        logger.info("###########################################svn测试删除仓库")
        logger.info("\nSVN删除仓库操作结果: %s", json.dumps(result))
        # 验证更新结果
        assert result["status"] == "success"
        assert not self.repo_path.exists()

    @classmethod
    def teardown_class(cls):
        """测试清理"""
        cls.svn.destroy_repository()
        assert not TEST_LOCAL_PATH.exists()
        # 注意：SVN工作副本(.svn目录)需要特殊处理
        logger.info(f"\n测试完成，请手动检查目录：{TEST_LOCAL_PATH}")


if __name__ == "__main__":
    # 创建测试实例
    tester = TestSVNVersionControl()
    tester.setup_class()

    try:
        print("\n=== 开始执行测试 ===")

        # # 1. 清理环境
        # tester.test_destroy_after_checkout()

        # # 2. 测试检出仓库
        # tester.test_checkout_repository()

        # 3. 测试获取版本变更
        tester.test_get_changes_between_revisions()

        # # 4. 测试更新仓库
        # tester.test_update_repository()

        # # 5. 测试删除仓库
        # tester.test_destroy_after_checkout()

        print("\n=== 测试全部通过 ===")
    except Exception as e:
        logger.error(f"测试失败: {str(e)}", exc_info=True)
        print(f"\n!!! 测试失败: {str(e)}")
    finally:
        # 清理环境
        tester.teardown_class()
        print("\n测试完成，清理环境")
