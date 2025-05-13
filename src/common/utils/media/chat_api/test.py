import ctypes
import sys
import subprocess

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    # 重新启动脚本，以管理员身份运行
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
else:
    # 以管理员身份运行的代码
    print("Running with admin privileges.")
    # 执行需要管理员权限的操作
    

def run_as_admin(command):
    if sys.platform == "win32":
        # 使用 runas 命令以管理员身份运行
        subprocess.run(['runas', '/user:Administrator', command])
    else:
        print("This function is only supported on Windows.")

# 示例：以管理员身份运行一个命令
run_as_admin('cmd.exe /c "ipconfig /all"')