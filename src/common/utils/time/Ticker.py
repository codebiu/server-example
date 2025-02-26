import time
from functools import wraps

class Ticker:
    def __init__(self, reset=True) -> None:
        self.ts = time.perf_counter()
        self.reset = reset
        self.maps = {}

    def tick(self, name, reset=None):
        ts = time.perf_counter()
        if reset is None:
            reset = self.reset
        dt = ts - self.ts
        if reset:
            self.ts = ts
        self.maps[name] = dt
        return dt
    
def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()  # 记录开始时间
        result = func(*args, **kwargs)  # 执行被装饰的函数
        end_time = time.time()  # 记录结束时间
        print(f"Function {func.__name__} took {end_time - start_time:.4f} seconds to execute.")
        return result
    return wrapper

    
if __name__ == "__main__":
    # 创建 Ticker 实例
    ticker = Ticker()

    # 模拟一些操作
    time.sleep(3)
    dt1 = ticker.tick('operation1', reset=False)

    time.sleep(1)
    dt2 = ticker.tick('operation2', reset=True)
    
    time.sleep(1)
    dt3 = ticker.tick('operation3', reset=False)

    # 输出结果
    print(f"Time for operation1: {dt1:.6f} seconds")
    print(f"Time for operation2: {dt2:.6f} seconds")
    print(f"Time for operation3: {dt3:.6f} seconds")
    