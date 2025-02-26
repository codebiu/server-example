import sys
import platform
import subprocess


def find_and_kill_process(port, os_type):
    if os_type == "Windows":
        try:
            output = subprocess.check_output(f'netstat -aon | findstr :{port}', shell=True).decode()
            pids = [line.split()[-1] for line in output.splitlines() if 'LISTENING' in line]
        except subprocess.CalledProcessError:
            print(f"没有发现[{port}]端口被占用.")
            return

        for pid in pids:
            subprocess.run(f'taskkill /F /PID {pid}', shell=True, check=True)
        print(f"成功清理了[{port}]端口.")

    elif os_type in ["Darwin", "Linux"]:
        try:
            output = subprocess.check_output(f'lsof -i tcp:{port} -sTCP:LISTEN', shell=True).decode()
            pids = [line.split()[1] for line in output.splitlines()[1:]]
        except subprocess.CalledProcessError:
            print(f"没有找到占用[{port}]的端口.")
            return

        for pid in pids:
            subprocess.run(f'kill -9 {pid}', shell=True, check=True)
        print(f"成功杀死占用[{port}]的端口.")

    else:
        print("不支持的操作系统.")


if __name__ == '__main__':
    os_type = platform.system()
    port = sys.argv[1] if len(sys.argv) > 1 else 6666  # 默认端口

    print(f"系统类型: {os_type}, 端口号: {port}")
    find_and_kill_process(port, os_type)