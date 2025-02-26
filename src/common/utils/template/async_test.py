import asyncio
import time


async def task(name):
    print(f'Task {name} started at {time.strftime("%X")}')
    await asyncio.sleep(1)  # 模拟耗时一秒的操作
    print(f'Task {name} finished at {time.strftime("%X")}')


async def main():
    start_time = time.time()

    # # 创建任务列表
    # tasks = [task(f"task-{i}") for i in range(1, 6)]
    tasks = []
    for i in range(1, 6):
        t = task(f"task-{i}")
        tasks.append(t)
    # 并发执行所有任务
    await asyncio.gather(*tasks)
    
    print(f"All tasks completed in {time.time() - start_time:.2f} seconds")
    
    
    start_time = time.time()
    # 同步化
    for i in range(1, 6):
        await task(f"task-{i}")
    print(f"All tasks completed in {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
