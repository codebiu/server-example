from pathlib import Path
from datetime import datetime
from svn.remote import RemoteClient
from svn.local import LocalClient
from common.utils.code.version_control.version_control_interface import (
    VersionControlInterface,
)


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

            # 递归删除整个目录
            import shutil

            shutil.rmtree(self.repo_path)

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
                changes = self._get_changes_between_revisions(
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

    def _get_changes_between_revisions(self, old_rev: str, new_rev: str) -> list:
        """获取两个版本之间的变更文件列表"""
        try:
            log = self.client.log_default(revision_from=old_rev, revision_to=new_rev)
            changes = []
            for entry in log:
                changes.extend(entry.changelist.keys())
            return list(set(changes))  # 去重
        except Exception:
            return []

    def commit(self, message: str, files: list[str] = None) -> dict:
        """提交更改到SVN仓库"""
        try:
            self._ensure_client_initialized()

            if files:
                for file in files:
                    self.client.add(file)
            else:
                # SVN没有直接等同于git add -A的命令
                # 需要手动添加新文件和删除已删除文件
                self.client.add(".", force=True)
                # 删除操作需要单独处理

            self.client.commit(message=message)

            info = self.client.info()
            return {
                "status": "success",
                "message": "提交成功",
                "current_version": str(info["commit_revision"]),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat(),
            }

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
            return []

    def get_remote_versions(self, limit: int = 10) -> list[dict]:
        """获取远程SVN版本历史"""
        try:
            self._ensure_client_initialized()
            # SVN本地和远程日志通常相同
            return self.get_local_versions(limit)
        except Exception as e:
            return []

    def get_diff(self, version1: str, version2: str) -> list[str]:
        """获取两个SVN版本之间的差异"""
        try:
            self._ensure_client_initialized()
            diff = self.client.diff_summary(version1, version2)
            return [f"{item.kind}: {item.path}" for item in diff]
        except Exception as e:
            return [str(e)]

    def get_file_diff(self, file_path: str, version1: str, version2: str) -> list[str]:
        """获取文件在两个SVN版本之间的差异"""
        try:
            self._ensure_client_initialized()
            diff = self.client.diff(version1, version2, file_path)
            return diff.splitlines() if diff else []
        except Exception as e:
            return [str(e)]

 