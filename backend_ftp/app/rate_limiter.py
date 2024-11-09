# rate_limiter.py

import time
from threading import Lock


class TokenBucket:
    """
    令牌桶算法实现带宽限制
    rate: 每秒允许的字节数 (bytes/second)
    capacity: 桶的容量 (最大字节数)
    """

    def __init__(self, rate, capacity):
        self.rate = rate  # 令牌生成速率 (bytes/second)
        self.capacity = capacity  # 桶容量 (bytes)
        self.tokens = capacity  # 当前令牌数
        self.last_update = time.time()  # 上次更新时间
        self.lock = Lock()  # 线程锁

    def _add_tokens(self):
        """添加令牌"""
        now = time.time()
        time_passed = now - self.last_update
        new_tokens = time_passed * self.rate

        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_update = now

    def consume(self, bytes_count):
        """
        消耗令牌
        bytes_count: 需要消耗的字节数
        返回等待时间(秒)
        """
        with self.lock:
            self._add_tokens()

            if self.tokens >= bytes_count:
                self.tokens -= bytes_count
                return 0

            # 计算需要等待的时间
            required_tokens = bytes_count - self.tokens
            wait_time = required_tokens / self.rate

            # 更新令牌数和时间
            self.tokens = 0
            self.last_update = time.time() + wait_time

            return wait_time


def create_rate_limiter(user_type):
    """
    根据用户类型创建相应的速率限制器
    """
    # 定义不同用户类型的带宽限制 (bytes/second)
    BANDWIDTH_LIMITS = {
        'regular': 0.05 * 1024 * 1024,  # 0.2 MB/s
        'vip': 5 * 1024 * 1024,  # 5 MB/s
        'svip': 10 * 1024 * 1024  # 10 MB/s
    }

    rate = BANDWIDTH_LIMITS.get(user_type, 1024 * 1024)  # 默认 1 MB/s
    # 设置桶容量为速率的2倍，允许短时突发
    capacity = rate * 2

    return TokenBucket(rate, capacity)
