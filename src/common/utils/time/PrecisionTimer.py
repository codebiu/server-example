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
        if self.unit not in self.UNITS:
            raise ValueError(f"不支持的时间单位: {unit}。支持的单位: {list(self.UNITS.keys())}")
        self.logger = logger or print
        self._start = None
        self._end = None
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        if exc_type is None:  # 如果没有异常才记录时间
            result = self.result()
            output = f"[{result.name}] 耗时: {result.elapsed:.2f}{result.unit}"
            self.logger(output)
        return False
    
    def __call__(self, func):
        """使实例可作为装饰器使用"""
        @wraps(func)
        def wrapped(*args,**kwargs):
            with self:
                return func(*args,**kwargs)
        return wrapped
    
    def start(self) -> 'PrecisionTimer':
        """启动计时器"""
        if self._start is not None:
            raise RuntimeError("计时器已经启动")
        self._start = time.perf_counter_ns()
        self._end = None
        return self
    
    def stop(self) -> 'PrecisionTimer':
        """停止计时器"""
        if self._start is None:
            raise RuntimeError("计时器尚未启动")
        if self._end is not None:
            raise RuntimeError("计时器已经停止")
        self._end = time.perf_counter_ns()
        return self
    
    def result(self) -> BenchmarkResult:
        """获取计时结果（要求计时器已停止）"""
        if self._start is None:
            raise RuntimeError("计时器尚未启动")
        if self._end is None:
            raise RuntimeError("计时器尚未停止")
            
        elapsed_ns = self._end - self._start
        scale = self.UNITS[self.unit]
        elapsed = elapsed_ns / 1e9 * scale
        return BenchmarkResult(self.name, elapsed, self.unit)
    
    def elapsed(self, unit: str = None) -> float:
        """获取经过的时间（可以在计时器运行中调用）"""
        unit = unit or self.unit
        if unit not in self.UNITS:
            raise ValueError(f"不支持的时间单位: {unit}")
        
        if self._start is None:
            raise RuntimeError("计时器尚未启动")
            
        # 如果计时器未停止，使用当前时间计算
        end_time = self._end if self._end is not None else time.perf_counter_ns()
        elapsed_ns = end_time - self._start
        scale = self.UNITS[unit]
        return elapsed_ns / 1e9 * scale

if __name__ == "__main__":
    from config.log import logger

    # 测试各种使用方式
    try:
        with PrecisionTimer("测试", unit="invalid"):
            pass
    except ValueError as e:
        logger.error(e)

    with PrecisionTimer("测试"):
        time.sleep(0.1)
    
    with PrecisionTimer("图像处理", unit="ms", logger=logger.info):
        time.sleep(0.1)
    
    timer = PrecisionTimer("算法测试").start()
    time.sleep(0.1)
    result = timer.stop().result()
    logger.info(result)

    # 作为实例装饰器
    @PrecisionTimer("数据清洗", unit='s')
    def clean_data():
        time.sleep(0.1)

    clean_data()  # 输出: [数据清洗] 耗时: 0.10s

    # 作为上下文管理器
    with PrecisionTimer("图像处理", unit='ms') as timer:
        time.sleep(0.1)
        logger.info(f"运行中已耗时: {timer.elapsed('ms'):.2f}ms")  # 现在可以安全调用
    logger.info(f"最终耗时: {timer.elapsed('ms'):.2f}ms")