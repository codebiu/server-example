import time
import threading

# 用于定时输出当前时间
def print_time():
    while True:
        # 获取当前时间
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f"当前时间: {current_time}")
        time.sleep(5)  # 每秒钟输出一次

# 用于接收用户输入
def get_user_input():
    while True:
        user_input = input("请输入内容：")
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f"时间: {current_time}, 你输入的内容是: {user_input}")

# 创建并启动线程
time_thread = threading.Thread(target=print_time, daemon=True)
input_thread = threading.Thread(target=get_user_input, daemon=True)

time_thread.start()
input_thread.start()

# 让主线程一直保持运行，防止程序退出
while True:
    time.sleep(1)
