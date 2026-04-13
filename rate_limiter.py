"""
蜻蜓数据API - 速率限制器
"""
import time
from collections import defaultdict
from threading import Lock
from config import RATE_LIMIT_MINUTE, RATE_LIMIT_DAY, RATE_LIMIT_MONTH


class RateLimiter:
    """滑动窗口速率限制器"""

    def __init__(self):
        # 每分钟请求计数
        self.minute_buckets = defaultdict(list)
        # 每天请求计数
        self.day_buckets = defaultdict(list)
        # 每月请求计数
        self.month_buckets = defaultdict(list)
        # 锁
        self.lock = Lock()
        # 限速标记
        self.rate_limited = defaultdict(lambda: None)

    def _clean_old(self, buckets, window_seconds):
        """清理过期的请求记录"""
        now = time.time()
        cutoff = now - window_seconds
        return {k: [t for t in v if t > cutoff] for k, v in buckets.items()}

    def _add_request(self, buckets, key, timestamp=None):
        """添加请求记录"""
        now = timestamp or time.time()
        buckets[key].append(now)

    def check_and_record(self, token: str) -> tuple[bool, str, dict]:
        """
        检查并记录请求

        Returns:
            (is_allowed, message, rate_info)
        """
        with self.lock:
            now = time.time()
            minute = 60
            day = 86400
            month = 2592000

            # 清理过期记录
            self.minute_buckets = self._clean_old(self.minute_buckets, minute)
            self.day_buckets = self._clean_old(self.day_buckets, day)
            self.month_buckets = self._clean_old(self.month_buckets, month)

            # 检查每分钟限制
            minute_count = len(self.minute_buckets[token])
            if minute_count >= RATE_LIMIT_MINUTE:
                self.rate_limited[token] = now + 60
                return False, f"请求过于频繁，请等待60秒", {
                    "retry_after": 60,
                    "limit": RATE_LIMIT_MINUTE,
                }

            # 检查每日限制
            day_count = len(self.day_buckets[token])
            if day_count >= RATE_LIMIT_DAY:
                return False, f"今日查询次数已用完（每日{RATE_LIMIT_DAY}次）", {
                    "limit": RATE_LIMIT_DAY,
                    "used": day_count,
                }

            # 检查每月限制
            month_count = len(self.month_buckets[token])
            if month_count >= RATE_LIMIT_MONTH:
                return False, f"本月查询次数已用完（每月{RATE_LIMIT_MONTH}次）", {
                    "limit": RATE_LIMIT_MONTH,
                    "used": month_count,
                }

            # 记录请求
            self._add_request(self.minute_buckets, token, now)
            self._add_request(self.day_buckets, token, now)
            self._add_request(self.month_buckets, token, now)

            return True, "OK", {
                "minute_remaining": RATE_LIMIT_MINUTE - minute_count - 1,
                "daily_remaining": RATE_LIMIT_DAY - day_count - 1,
                "monthly_remaining": RATE_LIMIT_MONTH - month_count - 1,
            }

    def is_rate_limited(self, token: str) -> bool:
        """检查是否被限速"""
        limited_until = self.rate_limited.get(token)
        if limited_until and time.time() < limited_until:
            return True
        if token in self.minute_buckets:
            minute_count = len([t for t in self.minute_buckets[token] if time.time() - t < 60])
            if minute_count >= RATE_LIMIT_MINUTE:
                return True
        return False

    def get_status(self, token: str) -> dict:
        """获取速率状态"""
        now = time.time()
        minute_count = len([t for t in self.minute_buckets.get(token, []) if now - t < 60])
        day_count = len([t for t in self.day_buckets.get(token, []) if now - t < 86400])
        month_count = len([t for t in self.month_buckets.get(token, []) if now - t < 2592000])

        return {
            "minute_used": minute_count,
            "minute_limit": RATE_LIMIT_MINUTE,
            "daily_used": day_count,
            "daily_limit": RATE_LIMIT_DAY,
            "monthly_used": month_count,
            "monthly_limit": RATE_LIMIT_MONTH,
        }


# 全局实例
_global_limiter = None


def get_limiter() -> RateLimiter:
    """获取全局限制器实例"""
    global _global_limiter
    if _global_limiter is None:
        _global_limiter = RateLimiter()
    return _global_limiter
