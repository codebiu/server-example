from pathlib import Path
import asyncio
import subprocess
import shutil

class GitUtils:
    '''单个git库对象'''
    def __init__(self, temp_dir: Path, repo: str):
        self.temp_dir = temp_dir
        self.repo: str = repo
        self.repo_name: str = GitUtils.get_repo_name(repo)
        self.project_dir: Path = temp_dir / self.repo_name

    async def git_clone(self):
        '''
        Clones a git repository into a temporary directory with progress display
        克隆一个git仓库到临时目录并显示进度
        '''
        try:
            print(f"Cloning {self.repo} into {str(self.project_dir)}")
            
            # 如果目标目录已存在则跳过克隆
            if self.project_dir.exists():
                yield f"Repository already exists in {str(self.project_dir)}, skipping clone."
                return
            
            # 确保临时目录存在
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            
            process = await asyncio.create_subprocess_exec(
                "git", "clone", "--progress", self.repo, str(self.project_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            
            # 实时输出进度信息
            while True:
                output = await process.stdout.read(4096)
                # output = await process.stdout.readline()
                if output == '' and process.returncode is not None:
                    break
                if output:
                    # 替换 \r 为 \n
                    output = output.decode().replace("\r", "\n").strip()
                    
                        
                    yield output
            
            # 检查返回码
            await process.wait()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(
                    process.returncode, 
                    process.args,
                    f"克隆失败 {process.returncode}"
                )
                
            print(f"Successfully cloned {self.repo}")
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to clone repository {self.repo}")
            # 包装异常并抛出
            raise RuntimeError(f"Git clone failed: {str(e)}") from e
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise

    def delete(self):
        '''删除临时目录'''
        if self.project_dir.exists():
            shutil.rmtree(self.project_dir)  # 递归删除文件夹及其内容
            print(f"Deleted temporary directory {str(self.project_dir)}")
        else:
            print(f"Temporary directory {str(self.project_dir)} does not exist")
            
    @staticmethod
    def get_repo_name(repo: str):
        '''提取仓库名称'''
        repo_name = repo.split('/')[-1].replace('.git', '')
        return repo_name

# 示例用法
if __name__ == "__main__":
# 示例用法
    from config.path import dir_temp
    from config.log import logger
    repo_url = "https://github.com/tree-sitter/tree-sitter-cpp.git"
    temp_directory = Path(dir_temp)
 
    async def main():
        git_utils = GitUtils(temp_directory, repo_url)
        try:
            async for message in git_utils.git_clone():
                logger.info(message)
        except RuntimeError as e:
            print(f"克隆失败，请检查网络和仓库地址: {str(e)}")

    asyncio.run(main())
