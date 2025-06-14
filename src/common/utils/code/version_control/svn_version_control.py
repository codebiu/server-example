from pathlib import Path
from datetime import datetime
from svn.remote import RemoteClient
from svn.local import LocalClient
from common.utils.code.version_control.svn_tools.svn_ex import SvnEx
from common.utils.code.version_control.version_control_interface import (
    VersionControlInterface,
)
from common.utils.file.dir_manager import DirManager


class SVNVersionControl(VersionControlInterface):
    """SVN版本控制实现类（使用svn库）"""

    def __init__(self, repo_path: Path, username: str = None, password: str = None):
        """初始化SVN客户端"""
        self.repo_path = repo_path.absolute()
        self.username = username
        self.password = password
        self.client = None

        # 检查是否已有仓库
        if (self.repo_path / ".svn").exists():
            try:
                self.client = LocalClient(
                    str(self.repo_path), username=self.username, password=self.password
                )
                self.client.info()  # 测试连接
            except Exception:
                self.client = None

    def clone_or_checkout(self, repo_url: str, revision: str = None) -> dict:
        """克隆/检出SVN仓库"""
        try:
            if self.client:
                # 已有仓库，返回提示信息建议更新
                info = self.client.info()
                return {
                    "status": "info",
                    "message": "仓库已存在，建议使用update方法更新",
                    "path": str(self.repo_path),
                    "current_version": {
                        "id": str(info["commit_revision"]),
                        "url": info["url"],
                    },
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                # 新检出
                self.repo_path.mkdir(parents=True, exist_ok=True)
                # auth_url = self._get_authenticated_url(repo_url)
                client = RemoteClient(
                    repo_url, username=self.username, password=self.password
                )
                client.checkout(str(self.repo_path), revision=revision)

                # 更新客户端实例
                self.client = LocalClient(
                    str(self.repo_path), username=self.username, password=self.password
                )

                info = self.client.info()
                return {
                    "status": "success",
                    "message": "仓库检出成功",
                    "path": str(self.repo_path),
                    "current_version": {
                        "id": str(info["commit_revision"]),
                        "url": info["url"],
                    },
                    "timestamp": datetime.now().isoformat(),
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "path": str(self.repo_path),
                "timestamp": datetime.now().isoformat(),
            }

    def destroy_repository(self) -> dict:
        """
        销毁SVN仓库（删除整个仓库目录）

        返回:
            dict: 包含操作状态的字典
            {
                "status": "success"|"error",
                "message": str,
                "path": str,
                "timestamp": str
            }
        """
        try:
            if not self.repo_path.exists():
                return {
                    "status": "error",
                    "message": "仓库路径不存在",
                    "path": str(self.repo_path),
                    "timestamp": datetime.now().isoformat(),
                }

            # 关闭客户端
            self.client = None
            # 删除整个目录
            DirManager.remove_dir(self.repo_path)
            return {
                "status": "success",
                "message": "仓库删除成功",
                "path": str(self.repo_path),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"仓库删除失败: {str(e)}",
                "path": str(self.repo_path),
                "timestamp": datetime.now().isoformat(),
            }

    def _ensure_client_initialized(self):
        """确保客户端已初始化"""
        if not self.client:
            raise ValueError("SVN客户端未初始化，请先执行clone_or_checkout")

    def update(self, revision: str = None) -> dict:
        """更新本地SVN仓库"""
        try:
            self._ensure_client_initialized()

            old_info = self.client.info()
            self.client.update(revision=revision)
            new_info = self.client.info()
            changes = []
            if old_info["commit_revision"] != new_info["commit_revision"]:
                # 获取变更文件列表（SVN需要特殊处理）
                changes = self.get_changes_between_revisions(
                    str(old_info["commit_revision"]), str(new_info["commit_revision"])
                )

            return {
                "status": "success",
                "message": "仓库更新成功",
                "path": str(self.repo_path),
                "changes": changes,
                "old_version": str(old_info["commit_revision"]),
                "new_version": str(new_info["commit_revision"]),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "path": str(self.repo_path),
                "timestamp": datetime.now().isoformat(),
            }

    def get_changes_between_revisions(self, old_rev: str, new_rev: str,encoding="utf-8") -> list:
        """获取两个版本之间的变更文件列表"""
        try:
            logs = list(
                SvnEx.get_svn_logs(
                    self.repo_path,
                    revision_from=old_rev,
                    revision_to=new_rev,
                    changelist = True,
                    encoding=encoding
                )
            )
            changes = []
            # 版本修改收集
            # A：新增文件
            # M：修改文件
            # D：删除文件
            # R：替换文件
            for log in logs:
                changes.extend(log.changelist)
            return changes
        except Exception as e:
            print(
                f"Error getting changes between revisions {old_rev} and {new_rev}: {e}"
            )
            return []

    def commit(self, message: str, files: list[str] = None) -> dict:
        """提交更改到SVN仓库"""
        pass
        # try:
        #     self._ensure_client_initialized()

        #     if files:
        #         for file in files:
        #             self.client.add(file)
        #     else:
        #         # SVN没有直接等同于git add -A的命令
        #         # 需要手动添加新文件和删除已删除文件
        #         self.client.add(".", force=True)
        #         # 删除操作需要单独处理

        #     self.client.commit(message=message)

        #     info = self.client.info()
        #     return {
        #         "status": "success",
        #         "message": "提交成功",
        #         "current_version": str(info["commit_revision"]),
        #         "timestamp": datetime.now().isoformat(),
        #     }
        # except Exception as e:
        #     return {
        #         "status": "error",
        #         "message": str(e),
        #         "timestamp": datetime.now().isoformat(),
        #     }

    def get_local_versions(self, limit: int = 10) -> list[dict]:
        """获取本地SVN版本历史"""
        try:
            self._ensure_client_initialized()
            log_entries = self.client.log_default(limit=limit)

            versions = []
            for entry in log_entries:
                versions.append(
                    {
                        "id": str(entry.revision),
                        "message": entry.msg.strip(),
                        "author": entry.author,
                        "date": entry.date.isoformat(),
                    }
                )
            return versions
        except Exception as e:
            return [str(e)]



    def get_diff(self, version1: str, version2: str, file_path: str = None) -> list[str]:
        """获取两个SVN版本之间的差异"""
        try:
            self._ensure_client_initialized()
            diff = SvnEx.diff(self.repo_path,version1, version2)
            return diff
        except Exception as e:
            return [str(e)]
        
    def get_remote_versions(self, limit: int = 10) -> list[dict]:
        """获取远程SVN版本历史"""
        try:
            self._ensure_client_initialized()
            # SVN本地和远程日志通常相同
            return self.get_local_versions(limit)
        except Exception as e:
            return [str(e)]

if __name__ == "__main__":
    from config.path import dir_test

    # 测试配置
    TEST_SVN_URL = "https://A52230321050007/svn/test_svn_project1/"  # 本地SVN服务地址
    TEST_LOCAL_PATH = dir_test / "svn_test_repo"
    TEST_BRANCH = "HEAD"
    TEST_USERNAME = "wx"  # SVN账号
    TEST_PASSWORD = "123"  # SVN密码
    svn = SVNVersionControl(TEST_LOCAL_PATH)
    # print(svn.update())
    print(svn.update())
