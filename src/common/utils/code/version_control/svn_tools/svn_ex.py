from dataclasses import dataclass
import subprocess
from xml.etree import ElementTree
import dateutil.parser
from datetime import datetime


@dataclass
class LogEntry:
    """SVN日志条目（自动生成__repr__和__init__）"""

    revision: int
    author: str
    date: datetime
    msg: str
    changelist: list[tuple[str, str]] | None  # (action, path)


class SvnEx:
    """SVN日志查询工具（无冗余类型注解版）"""

    @staticmethod
    def get_svn_logs(
        repo_path,
        timestamp_from_dt=None,
        timestamp_to_dt=None,
        limit=None,
        rel_filepath=None,
        stop_on_copy=False,
        revision_from=None,
        revision_to=None,
        changelist=False,
        use_merge_history=False,
        encoding="utf-8",
    ):
        """
        获取SVN日志（Python 3.10+ 简洁版）

        参数:
            repo_path: 仓库路径
            changelist: 是否返回文件变更
            ...其他参数同原版

        返回:
            生成LogEntry对象的生成器
        """
        # 构建命令参数
        args = [
            "svn",
            "log",
            "--xml",
            (f"{repo_path}/{rel_filepath}" if rel_filepath else repo_path),
        ]

        # 处理时间/版本范围
        if timestamp_from_dt:
            time_range = f"{{{timestamp_from_dt.isoformat()}}}:{timestamp_to_dt and f'{{{timestamp_to_dt.isoformat()}}}' or 'HEAD'}"
            args.extend(("-r", time_range))
        elif revision_from or revision_to:
            args.extend(("-r", f"{revision_from or '1'}:{revision_to or 'HEAD'}"))

        # 添加可选参数
        args.extend(
            [
                *(["-l", str(limit)] if limit else []),
                *(["--stop-on-copy"] if stop_on_copy else []),
                *(["--use-merge-history"] if use_merge_history else []),
                *(["--verbose"] if changelist else []),
            ]
        )

        # 执行命令并解析
        try:
            result = subprocess.run(
                args,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding=encoding,  # 替代单独的decode()
            )
            for entry in ElementTree.fromstring(result.stdout).iter("logentry"):
                paths = entry.find("paths")
                yield LogEntry(
                    revision=int(entry.get("revision")),
                    author=(entry.find("author").text or ""),
                    date=dateutil.parser.parse(entry.find("date").text),
                    msg=(entry.find("msg").text or ""),
                    changelist=[(p.attrib["action"], p.text) for p in paths]
                    if changelist and paths
                    else None,
                )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"SVN命令失败: {e.stderr}")

    def diff(
        repo_path,
        old_rev,
        new_rev,
        rel_filepath=None,
        encoding="utf-8",
    ):
        """
        获取两个版本间的差异内容（带行列信息）

        参数:
            repo_path
            old_rev: 旧版本号
            new_rev: 新版本号
            rel_filepath: 可选，指定相对路径时只比较单个文件

        返回:
            {
                "文件路径1": [
                    {
                        "old_start": 起始行号,
                        "old_lines": 影响行数,
                        "new_start": 起始行号,
                        "new_lines": 影响行数,
                        "changes": ["-删除行", "+新增行", " 未修改行"]
                    },
                    ...
                ],
                "文件路径2": [...]
            }
        """
        # 构建SVN命令
        cmd = ["svn", "diff", "-r", f"{old_rev}:{new_rev}"]
        if rel_filepath:
            cmd.append(f"{repo_path}/{rel_filepath}")
        else:
            cmd.append(repo_path)

        # 执行命令
        try:
            result = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding=encoding,
            )
            diff_output = result.stdout
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:  # diff有差异时的正常返回码
                diff_output = e.stdout
            else:
                raise RuntimeError(f"SVN差异比较失败: {e.stderr}")

        # 解析diff输出
        diffs = {}
        current_file = None
        current_hunk = None

        for line in diff_output.splitlines():
            # 检测文件头
            if line.startswith("Index: "):
                current_file = line[7:].strip()
                diffs[current_file] = []

            # 检测差异块头
            elif line.startswith("@@ "):
                if current_file:
                    # 解析行号信息: @@ -旧开始,旧行数 +新开始,新行数 @@
                    parts = line[3:].split("@@")[0].split()
                    old_info = parts[0].split(",")
                    new_info = parts[1].split(",")

                    current_hunk = {
                        "old_start": int(old_info[0][1:]),
                        "old_lines": int(old_info[1]) if len(old_info) > 1 else 1,
                        "new_start": int(new_info[0][1:]),
                        "new_lines": int(new_info[1]) if len(new_info) > 1 else 1,
                        "changes": {"added": "", "removed": ""},
                    }
                    diffs[current_file].append(current_hunk)

            # 收集差异内容（只记录实际修改的行）
            elif current_hunk:
                if line.startswith("+") and not line.startswith("+++ "):
                    # 去掉开头的+号，保留新增内容
                    current_hunk["changes"]["added"] += line[1:]
                elif line.startswith("-") and not line.startswith("--- "):
                    # 去掉开头的-号，保留删除内容
                    current_hunk["changes"]["removed"] += line[1:]
                # 忽略以空格开头的上下文行和文件路径问题

        return diffs
    
    @staticmethod
    def get_local_version(repo_path, rel_filepath=None):
        """
        获取本地工作副本的当前版本号
        
        参数:
            repo_path: 仓库根路径
            rel_filepath: 可选，指定文件时获取该文件的本地版本
            
        返回:
            整数版本号（如 12345）
        """
        target = f"{repo_path}/{rel_filepath}" if rel_filepath else repo_path
        try:
            result = subprocess.run(
                ["svn", "info", "--show-item", "revision", target],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8"
            )
            return int(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"获取本地版本失败: {e.stderr}")

    @staticmethod
    def get_latest_version(repo_path, rel_filepath=None):
        """
        获取远程仓库的最新版本号
        
        参数:
            repo_path: 仓库URL或路径
            rel_filepath: 可选，指定文件时获取该文件的最新版本
            
        返回:
            整数版本号（如 12345）
        """
        target = f"{repo_path}/{rel_filepath}" if rel_filepath else repo_path
        try:
            result = subprocess.run(
                ["svn", "info", "--show-item", "last-changed-revision", target],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8"
            )
            return int(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"获取最新版本失败: {e.stderr}")

    @staticmethod
    def get_version_status(repo_path, rel_filepath=None):
        """
        获取版本状态比较结果
        
        参数:
            repo_path: 仓库路径
            rel_filepath: 可选，指定文件时检查该文件
            
        返回:
            {
                "local": 本地版本,
                "latest": 最新版本,
                "status": "最新"|"需更新"|"冲突"|"未知"
            }
        """
        try:
            local = SvnEx.get_local_version(repo_path, rel_filepath)
            latest = SvnEx.get_latest_version(repo_path, rel_filepath)
            
            status = "最新" if local == latest else "需更新"
            if local > latest:  # 本地版本比服务器新（可能提交过但未更新）
                status = "冲突"
                
            return {
                "local": local,
                "latest": latest,
                "status": status
            }
        except Exception as e:
            return {
                "local": None,
                "latest": None,
                "status": f"错误: {str(e)}"
            }
            
    def get_svn_project_name(url):
        """
        从SVN仓库URL中提取项目名称

        参数:
            url (str): SVN仓库URL (例如: 'http://svn.example.com/repos/myproject/trunk')

        返回:
            str: 从URL中提取的项目名称
        """
        # 去除URL末尾可能存在的斜杠
        url = url.rstrip("/")

        # 将URL按斜杠分割成多个部分
        parts = url.split("/")

        # 项目名称通常是'trunk'、'branches'或'tags'之前的最后一部分
        # 我们从后向前查找第一个非标准目录名
        for part in reversed(parts):
            if part not in ("trunk", "branches", "tags", ""):
                return part

        # 如果没有找到项目名称，则返回最后一部分
        return parts[-1] if parts else ""

# 使用示例
if __name__ == "__main__":
    repo_path = "/path/to/repo"
    # logs = list(
    #     SvnEx.get_svn_logs(
    #         repo_path,
    #         revision_from=0,
    #         revision_to=1,
    #         changelist=True,
    #         encoding="utf-8",
    #     )
    # )
