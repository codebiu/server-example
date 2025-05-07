from pathlib import Path
from datetime import datetime
import shutil
import git
from typing import Optional, List, Dict
from common.utils.code.version_control.version_control_interface import VersionControlInterface

class GitVersionControl(VersionControlInterface):
    """Git版本控制实现类（使用GitPython库）"""

    def __init__(self, repo_path: Path, username: str = None, password: str = None):
        """初始化Git客户端"""
        self.repo_path = repo_path.absolute()
        self.username = username
        self.password = password
        self.repo: Optional[git.Repo] = None
        
        # 检查是否已有仓库
        if (self.repo_path / ".git").exists():
            try:
                self.repo = git.Repo(self.repo_path)
                if not self.repo.bare:
                    self.repo.git.status()
            except (git.InvalidGitRepositoryError, git.NoSuchPathError):
                self.repo = None

    def _get_authenticated_url(self, url: str) -> str:
        """获取带认证信息的URL"""
        if self.username and self.password:
            return url.replace('://', f'://{self.username}:{self.password}@')
        return url

    def clone_or_checkout(self, repo_url: str, branch: str = None) -> Dict:
        """克隆/检出Git仓库"""
        if self.repo:
            # 已有仓库，返回提示信息建议更新
            current_version = self.repo.head.commit.hexsha
            branch_name = self.repo.active_branch.name
            
            return {
                "status": "info",
                "message": "仓库已存在，建议使用update方法更新",
                "path": str(self.repo_path),
                "current_version": {"id": current_version, "branch": branch_name},
                "timestamp": datetime.now().isoformat(),
            }
        else:
            # 新克隆
            self.repo_path.mkdir(parents=True, exist_ok=True)
            auth_url = self._get_authenticated_url(repo_url)
            self.repo = git.Repo.clone_from(
                auth_url,
                self.repo_path,
                branch=branch if branch else None
            )
            
            current_version = self.repo.head.commit.hexsha
            branch_name = self.repo.active_branch.name
            
            return {
                "status": "success",
                "message": "仓库克隆成功",
                "path": str(self.repo_path),
                "current_version": {"id": current_version, "branch": branch_name},
                "timestamp": datetime.now().isoformat(),
            }

    def _ensure_repo_initialized(self):
        """确保仓库已初始化"""
        if not self.repo:
            raise ValueError("Git仓库未初始化，请先执行clone_or_checkout")

    def update(self) -> Dict:
        """更新本地Git仓库"""
        self._ensure_repo_initialized()
        
        old_version = self.repo.head.commit.hexsha
        self.repo.git.pull()
        new_version = self.repo.head.commit.hexsha
        
        changes = [
            diff.a_path for diff in self.repo.head.commit.diff(old_version)
        ]
        
        return {
            "status": "success",
            "message": "仓库更新成功",
            "path": str(self.repo_path),
            "changes": changes,
            "old_version": old_version,
            "new_version": new_version,
            "timestamp": datetime.now().isoformat(),
        }

    # 其他方法保持不变...
    def commit(self, message: str, files: List[str] = None) -> Dict:
        """提交更改到Git仓库"""
        self._ensure_repo_initialized()
        
        if files:
            self.repo.index.add(files)
        else:
            self.repo.git.add(A=True)

        self.repo.index.commit(message)
        
        return {
            "status": "success",
            "message": "提交成功",
            "current_version": self.repo.head.commit.hexsha,
            "timestamp": datetime.now().isoformat(),
        }

    def get_local_versions(self, limit: int = 10) -> List[Dict]:
        """获取本地Git版本历史"""
        self._ensure_repo_initialized()
        return [
            {
                "id": commit.hexsha,
                "message": commit.message.strip(),
                "author": commit.author.name,
                "date": commit.committed_datetime.isoformat()
            }
            for commit in self.repo.iter_commits(max_count=limit)
        ]

    # 其他方法实现...

    def get_remote_versions(self, limit: int = 10) -> list[dict]:
        """获取远程Git版本历史"""
        # 先获取远程更新
        for remote in self.repo.remotes:
            remote.fetch()
        
        # 然后获取日志
        return self.get_local_versions(limit)

    def get_diff(self, version1: str, version2: str) -> list[str]:
        """获取两个Git版本之间的差异"""
        diff = self.repo.git.diff(version1, version2)
        return diff.splitlines() if diff else []

    def get_file_diff(self, file_path: str, version1: str, version2: str) -> list[str]:
        """获取文件在两个Git版本之间的差异"""
        diff = self.repo.git.diff(version1, version2, '--', file_path)
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
    
    def destroy_repository(self) -> Dict:
        """
        销毁Git仓库（删除整个仓库目录）
        
        返回:
            Dict: 包含操作状态的字典
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
                    "timestamp": datetime.now().isoformat()
                }

            # 关闭所有可能的文件句柄
            if self.repo:
                self.repo.close()
                self.repo = None

            # 递归删除整个目录
            shutil.rmtree(self.repo_path)

            return {
                "status": "success",
                "message": "仓库删除成功",
                "path": str(self.repo_path),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"仓库删除失败: {str(e)}",
                "path": str(self.repo_path),
                "timestamp": datetime.now().isoformat()
            }