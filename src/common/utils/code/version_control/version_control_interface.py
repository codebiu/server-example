from abc import ABC, abstractmethod
import difflib

class VersionControlInterface(ABC):
    """版本控制抽象基类
    
    定义了版本控制系统应实现的核心操作接口，包括：
    - 仓库初始化与检出
    - 版本管理
    - 差异比较
    - 提交与更新
    """
    
    @abstractmethod
    def __init__(self, repo_path, username=None, password=None):
        """初始化版本控制客户端
        
        Args:
            repo_path: 本地仓库路径
            username: 认证用户名(可选)
            password: 认证密码(可选)
            
        Raises:
            ValueError: 如果仓库路径无效或不是有效的版本控制仓库
        """
        pass
    
    @abstractmethod
    def clone_or_checkout(self, repo_url, branch=None):
        """克隆/检出仓库到本地
        
        Args:
            repo_url: 远程仓库URL
            branch: 分支/标签名(可选)
            
        Returns:
            dict: 包含操作结果的字典，至少包含:
                - status: 操作状态
                - path: 本地仓库路径
                - current_version: 当前版本信息
                - timestamp: 操作时间
        """
        pass
    
    @abstractmethod
    def update(self):
        """更新本地仓库到最新版本
        
        Returns:
            dict: 包含更新结果的字典，至少包含:
                - status: 操作状态
                - path: 本地仓库路径
                - changes: 变更列表
                - old_version: 更新前版本信息
                - new_version: 更新后版本信息
                - timestamp: 操作时间
        """
        pass
    
    @abstractmethod
    def commit(self, message, files=None):
        """提交更改到仓库
        
        Args:
            message: 提交信息
            files: 要提交的文件列表(可选，None表示提交所有变更)
            
        Returns:
            dict: 包含提交结果的字典，至少包含:
                - status: 操作状态
                - path: 本地仓库路径
                - current_version: 提交后的版本信息
                - timestamp: 操作时间
        """
        pass
    
    @abstractmethod
    def get_local_versions(self, limit=10):
        """获取本地版本历史
        
        Args:
            limit: 获取的版本数量限制
            
        Returns:
            list: 版本信息字典列表，每个字典至少包含:
                - id: 版本ID
                - message: 提交信息
                - author: 作者
                - date: 提交时间
        """
        pass
    
    @abstractmethod
    def get_remote_versions(self, limit=10):
        """获取远程版本历史
        
        Args:
            limit: 获取的版本数量限制
            
        Returns:
            list: 版本信息字典列表，格式同get_local_versions
        """
        pass
    
    @abstractmethod
    def get_diff(self, version1, version2):
        """获取两个版本之间的差异
        
        Args:
            version1: 起始版本标识
            version2: 结束版本标识
            
        Returns:
            list: 差异文本行列表
        """
        pass
    
    @abstractmethod
    def get_file_diff(self, file_path, version1, version2):
        """获取文件在两个版本之间的差异
        
        Args:
            file_path: 文件路径(相对仓库根目录)
            version1: 起始版本标识
            version2: 结束版本标识
            
        Returns:
            list: 差异文本行列表
        """
        pass
    
    @staticmethod
    def compare_files(file1, file2):
        """比较两个文件的差异
        
        Args:
            file1: 第一个文件路径
            file2: 第二个文件路径
            
        Returns:
            list: 差异文本行列表
        """
        with open(file1) as f1, open(file2) as f2:
            return list(difflib.unified_diff(
                f1.readlines(),
                f2.readlines(),
                fromfile=file1,
                tofile=file2
            ))