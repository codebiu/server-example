from pathlib import Path
from datetime import datetime
import pysvn
from common.utils.code.version_control.version_control_interface import VersionControlInterface

class SVNVersionControl(VersionControlInterface):
    """SVN版本控制实现类（使用pysvn库）"""

    def __init__(self, repo_path: str, username: str = None, password: str = None):
        """初始化SVN客户端"""
        self.repo_path = Path(repo_path).absolute()
        self.username = username
        self.password = password
        self.client = pysvn.Client()
        
        if username and password:
            self.client.set_default_username(username)
            self.client.set_default_password(password)
        
        # 验证是否是有效的SVN工作副本
        try:
            self.client.info(str(self.repo_path))
        except pysvn.ClientError:
            raise ValueError(f"路径 {self.repo_path} 不是有效的SVN工作副本")

    def _get_auth_options(self):
        """获取认证选项"""
        return pysvn.Revision(pysvn.opt_revision_kind.head)

    def checkout_or_update(self, repo_url: str, revision: str = None) -> dict:
        """检出/更新SVN仓库"""
        if not (self.repo_path / ".svn").exists():
            # 新检出
            rev = pysvn.Revision(pysvn.opt_revision_kind.number, revision) if revision else None
            self.client.checkout(repo_url, str(self.repo_path), revision=rev)
        else:
            # 已有工作副本，更新
            self.client.update(str(self.repo_path))
        
        # 获取当前版本信息
        info = self.client.info(str(self.repo_path))
        return {
            "status": "success",
            "path": str(self.repo_path),
            "current_version": {"id": str(info.revision.number), "url": info.url},
            "timestamp": datetime.now().isoformat(),
        }

    def update(self) -> dict:
        """更新本地工作副本"""
        info_before = self.client.info(str(self.repo_path))
        update_result = self.client.update(str(self.repo_path))
        info_after = self.client.info(str(self.repo_path))
        
        # 获取变更文件列表
        changes = []
        if update_result:
            changes = [item.path for item in self.client.diff_summarize(
                str(self.repo_path),
                revision1=pysvn.Revision(pysvn.opt_revision_kind.number, info_before.revision.number),
                revision2=pysvn.Revision(pysvn.opt_revision_kind.number, info_after.revision.number)
            )]
        
        return {
            "status": "success",
            "path": str(self.repo_path),
            "changes": changes,
            "old_version": str(info_before.revision.number),
            "new_version": str(info_after.revision.number),
            "timestamp": datetime.now().isoformat(),
        }

    def commit(self, message: str, files: list[str] = None) -> dict:
        """提交更改到SVN仓库"""
        # 添加文件到版本控制（如果需要）
        if files:
            for file in files:
                try:
                    self.client.add(Path(self.repo_path) / file)
                except pysvn.ClientError:
                    pass  # 文件可能已添加
        
        # 执行提交
        commit_info = self.client.checkin(
            [str(self.repo_path)] if files is None else [str(Path(self.repo_path) / f) for f in files],
            message
        )
        
        return {
            "status": "success",
            "path": str(self.repo_path),
            "current_version": str(commit_info.revision.number),
            "timestamp": datetime.now().isoformat(),
        }

    def get_local_versions(self, limit: int = 10) -> list[dict]:
        """获取本地版本历史"""
        log_messages = self.client.log(
            str(self.repo_path),
            limit=limit,
            discover_changed_paths=True
        )
        
        return [{
            "id": str(log.revision.number),
            "message": log.message.strip(),
            "author": log.author,
            "date": datetime.fromtimestamp(log.date).isoformat(),
            "changes": [p.path for p in log.changed_paths]
        } for log in log_messages]

    def get_remote_versions(self, limit: int = 10) -> list[dict]:
        """获取远程版本历史"""
        info = self.client.info(str(self.repo_path))
        log_messages = self.client.log(
            info.url,
            limit=limit,
            discover_changed_paths=True
        )
        
        return [{
            "id": str(log.revision.number),
            "message": log.message.strip(),
            "author": log.author,
            "date": datetime.fromtimestamp(log.date).isoformat(),
            "changes": [p.path for p in log.changed_paths]
        } for log in log_messages]

    def get_diff(self, version1: str, version2: str) -> list[str]:
        """获取两个版本之间的差异"""
        diff = self.client.diff(
            str(self.repo_path),
            revision1=pysvn.Revision(pysvn.opt_revision_kind.number, int(version1)),
            revision2=pysvn.Revision(pysvn.opt_revision_kind.number, int(version2))
        )
        return diff.splitlines() if diff else []

    def get_file_diff(self, file_path: str, version1: str, version2: str) -> list[str]:
        """获取文件在两个版本之间的差异"""
        full_path = str(Path(self.repo_path) / file_path)
        diff = self.client.diff(
            full_path,
            revision1=pysvn.Revision(pysvn.opt_revision_kind.number, int(version1)),
            revision2=pysvn.Revision(pysvn.opt_revision_kind.number, int(version2))
        )
        return diff.splitlines() if diff else []

    @classmethod
    def compare_files(cls, file1: str, file2: str) -> list[str]:
        """比较两个文件的差异"""
        import difflib
        with open(file1) as f1, open(file2) as f2:
            diff = difflib.unified_diff(
                f1.readlines(),
                f2.readlines(),
                fromfile=file1,
                tofile=file2
            )
        return list(diff)