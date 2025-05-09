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
        encoding='utf-8'
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
        args = ['svn', 'log', '--xml', (f"{repo_path}/{rel_filepath}" if rel_filepath else repo_path)]
        
        # 处理时间/版本范围
        if timestamp_from_dt:
            time_range = f"{{{timestamp_from_dt.isoformat()}}}:{timestamp_to_dt and f'{{{timestamp_to_dt.isoformat()}}}' or 'HEAD'}"
            args.extend(('-r', time_range))
        elif revision_from or revision_to:
            args.extend(('-r', f"{revision_from or '1'}:{revision_to or 'HEAD'}"))
        
        # 添加可选参数
        args.extend([
            *(['-l', str(limit)] if limit else []),
            *(['--stop-on-copy'] if stop_on_copy else []),
            *(['--use-merge-history'] if use_merge_history else []),
            *(['--verbose'] if changelist else [])
        ])

        # 执行命令并解析
        try:
            xml = subprocess.check_output(args, stderr=subprocess.PIPE).decode(encoding)
            for entry in ElementTree.fromstring(xml).iter('logentry'):
                paths = entry.find('paths')
                yield LogEntry(
                    revision=int(entry.get('revision')),
                    author=(entry.find('author').text or ''),
                    date=dateutil.parser.parse(entry.find('date').text),
                    msg=(entry.find('msg').text or ''),
                    changelist=[(p.attrib['action'], p.text) for p in paths] if changelist and paths else None
                )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"SVN命令失败: {e.stderr.decode(encoding)}")

# 使用示例
if __name__ == '__main__':
    for log in SvnEx.get_svn_logs('.', revision_from='1', changelist=True):
        print('-' * 50)
        print(log)  # 自动调用__str__