
import shutil
from common.utils.code.version_control.git_version_control import GitVersionControl
from config.path import dir_test

# 测试常量
TEST_REPO_URL = "https://github.com/ITILD/git_test.git"
TEST_LOCAL_PATH = dir_test / "git_test_repo"
TEST_BRANCH = "main"
# TEST_COMMIT_MESSAGE = "Test commit message"
# TEST_FILE = "test_file.txt"

class TestGitVersionControlRealRepo:
    """使用真实Git仓库进行测试"""

    @classmethod
    def setup_class(cls):
        """整个测试类初始化时执行一次"""
        cls.repo_path = TEST_LOCAL_PATH
        
        # 仅初始化GitVersionControl（整个测试类共享）
        cls.git_vc:GitVersionControl = GitVersionControl(cls.repo_path)
    def test_destroy_before_checkout(self):
        """测试强制删除仓库"""
        pass
        
        
    def test_clone_or_checkout_real(self):
        """测试克隆/检出真实仓库"""
        # 原生清理测试目录
        shutil.rmtree(self.repo_path)
        # 在此方法中执行克隆操作
        result = self.git_vc.clone_or_checkout(TEST_REPO_URL, TEST_BRANCH)
        print('###########################################测试克隆/检出真实仓库')
        print(result)
        assert result["status"] == "success"
        assert result["current_version"]["branch"] == TEST_BRANCH
        assert len(result["current_version"]["id"]) == 40  #