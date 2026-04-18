"""
限流模块测试
"""

import pytest
import time
from src.rate_limiter import RateLimiter, get_rate_limiter


class TestRateLimiter:
    """限流器测试"""

    def test_allow_requests(self):
        """测试允许请求"""
        limiter = RateLimiter()
        limiter.set_rule("test", requests=5, window=60)

        for i in range(5):
            allowed, remaining = limiter.check("client1", "test")
            assert allowed is True
            assert remaining == 4 - i

    def test_block_excess_requests(self):
        """测试阻止超额请求"""
        limiter = RateLimiter()
        limiter.set_rule("test", requests=3, window=60)

        # 发送3次请求
        for _ in range(3):
            limiter.check("client1", "test")

        # 第4次应该被阻止
        allowed, remaining = limiter.check("client1", "test")
        assert allowed is False
        assert remaining == 0

    def test_different_clients(self):
        """测试不同客户端独立计数"""
        limiter = RateLimiter()
        limiter.set_rule("test", requests=2, window=60)

        # 客户端1发送2次
        limiter.check("client1", "test")
        limiter.check("client1", "test")

        # 客户端2应该仍然可以
        allowed, _ = limiter.check("client2", "test")
        assert allowed is True

        # 客户端1应该被阻止
        allowed, _ = limiter.check("client1", "test")
        assert allowed is False

    def test_window_reset(self):
        """测试时间窗口重置"""
        limiter = RateLimiter()
        limiter.set_rule("test", requests=2, window=1)  # 1秒窗口

        # 发送2次请求
        limiter.check("client1", "test")
        limiter.check("client1", "test")

        # 应该被阻止
        allowed, _ = limiter.check("client1", "test")
        assert allowed is False

        # 等待窗口过期
        time.sleep(1.5)

        # 应该可以再次请求
        allowed, _ = limiter.check("client1", "test")
        assert allowed is True

    def test_get_stats(self):
        """测试获取统计"""
        limiter = RateLimiter()
        stats = limiter.get_stats()

        assert "total_clients" in stats
        assert "rules" in stats

    def test_get_client_info(self):
        """测试获取客户端信息"""
        limiter = RateLimiter()
        limiter.set_rule("test", requests=10, window=60)

        limiter.check("client1", "test")
        limiter.check("client1", "test")

        info = limiter.get_client_info("client1", "test")
        assert info["requests"] == 2
        assert info["limit"] == 10
        assert info["remaining"] == 8

    def test_singleton(self):
        """测试单例模式"""
        limiter1 = get_rate_limiter()
        limiter2 = get_rate_limiter()
        assert limiter1 is limiter2
