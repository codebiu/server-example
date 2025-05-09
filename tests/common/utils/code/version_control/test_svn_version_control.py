from pathlib import Path
from datetime import datetime
import shutil
import os,stat
import pytest
from config.path import dir_test
from common.utils.code.version_control.svn_version_control import SVNVersionControl

# 测试配置
TEST_SVN_URL = "https://A52230321050007/svn/test_svn_project1/"  # 本地SVN服务地址
TEST_LOCAL_PATH = dir_test / "svn_test_repo"
TEST_BRANCH ="HEAD"
TEST_USERNAME = "wx"                                # SVN账号
TEST_PASSWORD = "123"                               # SVN密码
TEST_FILE = "test_file.txt"                         # 测试文件名
TEST_COMMIT_MSG = "自动化测试提交"                   # 提交消息

class TestSVNVersionControl:
    """SVN版本控制完整测试"""
    
    @classmethod
    def setup_class(cls):
        """测试初始化"""
        cls.repo_path = TEST_LOCAL_PATH
        # 初始化SVN客户端
        cls.svn = SVNVersionControl(
            repo_path=TEST_LOCAL_PATH,
            username=TEST_USERNAME,
            password=TEST_PASSWORD
        )
    def test_destroy_before_checkout(self):
        """测试强制删除仓库"""
        path = self.repo_path
        DirManager.
        
     
    def test_checkout_repository(self):
        """测试首次检出仓库"""
        # 清理测试目录
        if self.repo_path.exists():
            shutil.rmtree(self.repo_path)
        
        # 首次检出
        result = self.svn.clone_or_checkout(
            repo_url=TEST_SVN_URL,
            revision=TEST_BRANCH
        )
        print('###########################################svn测试克隆/检出真实仓库')
        print('\nSVN检出操作结果:', result)  # 打印详细结果
        
        if result["status"] == "error":
            pytest.fail(f"SVN检出失败: {result['message']}")  # 明确显示错误原因
        
        assert result["status"] == "success"
        assert (self.repo_path / ".svn").exists()
        
    def test_destroy_after_checkout(self):
        """测试删除仓库"""
        result = self.svn.destroy_repository()
        print('###########################################svn测试删除仓库')
        print('\nSVN删除仓库操作结果:', result)
    
    
    @classmethod
    def teardown_class(cls):
        """测试清理"""
        # 删除测试文件（可选）
        test_file = TEST_LOCAL_PATH / TEST_FILE
        if test_file.exists():
            test_file.unlink()
        
        # 注意：SVN工作副本(.svn目录)需要特殊处理
        print(f"\n测试完成，请手动检查目录：{TEST_LOCAL_PATH}")

