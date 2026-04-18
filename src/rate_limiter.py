"""
API限流模块

保护API免受滥用。
"""

import time
from typing import Dict, Optional
from dataclasses import dataclass, field
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class RateLimitRule:
    """限流规则"""
    requests: int = 100  # 请求数
    window: int = 60     # 时间窗口（秒）


@dataclass
class ClientState:
    """客户端状态"""
    requests: int = 0
    window_start: float = field(default_factory=time.time)


class RateLimiter:
    """限流器"""

    def __init__(self):
        self._clients: Dict[str, ClientState] = defaultdict(ClientState)
        self._rules: Dict[str, RateLimitRule] = {
            "default": RateLimitRule(requests=100, window=60),
            "predict": RateLimitRule(requests=30, window=60),
            "batch": RateLimitRule(requests=10, window=60),
            "search": RateLimitRule(requests=50, window=60),
        }

    def set_rule(self, endpoint: str, requests: int, window: int) -> None:
        """设置限流规则"""
        self._rules[endpoint] = RateLimitRule(requests=requests, window=window)

    def check(self, client_id: str, endpoint: str = "default") -> tuple[bool, int]:
        """
        检查是否允许请求

        Returns:
            (allowed, remaining): 是否允许，剩余请求数
        """
        rule = self._rules.get(endpoint, self._rules["default"])
        state = self._clients[client_id]

        current_time = time.time()

        # 检查是否需要重置窗口
        if current_time - state.window_start > rule.window:
            state.requests = 0
            state.window_start = current_time

        # 检查是否超过限制
        if state.requests >= rule.requests:
            remaining = 0
            retry_after = int(rule.window - (current_time - state.window_start))
            return False, remaining

        # 增加请求计数
        state.requests += 1
        remaining = rule.requests - state.requests

        return True, remaining

    def get_client_info(self, client_id: str, endpoint: str = "default") -> Dict:
        """获取客户端限流信息"""
        rule = self._rules.get(endpoint, self._rules["default"])
        state = self._clients.get(client_id, ClientState())

        return {
            "requests": state.requests,
            "limit": rule.requests,
            "window": rule.window,
            "remaining": max(0, rule.requests - state.requests)
        }

    def cleanup_expired(self) -> int:
        """清理过期状态"""
        current_time = time.time()
        expired = []

        for client_id, state in self._clients.items():
            # 超过最大窗口时间的清理
            if current_time - state.window_start > 3600:
                expired.append(client_id)

        for client_id in expired:
            del self._clients[client_id]

        return len(expired)

    def get_stats(self) -> Dict:
        """获取限流统计"""
        return {
            "total_clients": len(self._clients),
            "rules": {
                k: {"requests": v.requests, "window": v.window}
                for k, v in self._rules.items()
            }
        }


# 全局限流器实例
_rate_limiter = None


def get_rate_limiter() -> RateLimiter:
    """获取限流器实例"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter
