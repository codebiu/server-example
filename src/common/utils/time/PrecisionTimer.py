import time
from dataclasses import dataclass
from typing import Callable, Optional, Any
from functools import wraps

@dataclass
class BenchmarkResult:
    name: str
    elapsed: float
    unit: str = "秒"

class PrecisionTimer:
    """高精度计时器，支持上下文管理器和装饰器两种模式"""
    
    UNITS = {
        's': 1,
        'ms': 1e3,
        'us': 1e6,
        'ns': 1e9
    }
    
    def __init__(self, name: str = "任务", unit: str = 'ms', logger: Optional[Callable] = None):
        self.name = name
        self.unit = unit.lower()
        self.logger = logger or print
        self._start = None
        self._end = None
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, *args):
        self.stop()
        result = self.result()
        output = f"[{result.name}] 耗时: {result.elapsed:.2f}{result.unit}"
        self.logger(output)
        return False
    
    def __call__(self, func):
        """使实例可作为装饰器使用"""
        @wraps(func)
        def wrapped(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return wrapped
    
    def start(self):
        self._start = time.perf_counter_ns()
        return self
    
    def stop(self):
        self._end = time.perf_counter_ns()
        return self
    
    def result(self) -> BenchmarkResult:
        elapsed_ns = self._end - self._start
        scale = self.UNITS.get(self.unit, 1e6)  # 默认毫秒
        elapsed = elapsed_ns / 1e9 * scale
        return BenchmarkResult(self.name, elapsed, self.unit)
    
    def elapsed(self, unit: str = None) -> float:
        unit = unit or self.unit
        return self.result().elapsed

if __name__ == "__main__":
    from config.log import logger

    with PrecisionTimer("测试"):
        time.sleep(1)
    with PrecisionTimer("图像处理", unit="ms", logger=logger.info):
        time.sleep(1)
    timer = PrecisionTimer("算法测试").start()
    time.sleep(1)
    result = timer.stop().result()
    # 方式1：作为实例装饰器
    @PrecisionTimer("数据清洗", unit='s')
    def clean_data():
        time.sleep(1.5)

    clean_data()  # 输出: [数据清洗] 耗时: 1.50s

    # 方式2：作为上下文管理器
    with PrecisionTimer("图像处理", unit='ms') as timer:
        time.sleep(1)
        print(f"已耗时: {timer.elapsed('ms'):.2f}ms")

