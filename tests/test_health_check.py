"""
健康检查模块测试
"""

import pytest
from src.health_check import HealthChecker, HealthStatus, get_health_checker


class TestHealthStatus:
    """健康状态测试"""

    def test_create_status(self):
        """测试创建状态"""
        status = HealthStatus(
            name="test",
            status="healthy",
            message="Test is healthy"
        )
        assert status.name == "test"
        assert status.status == "healthy"
        assert status.message == "Test is healthy"


class TestHealthChecker:
    """健康检查器测试"""

    def test_register_check(self):
        """测试注册检查"""
        checker = HealthChecker()

        def test_check():
            return HealthStatus(name="test", status="healthy")

        checker.register_check("test", test_check)
        assert "test" in checker.checks

    def test_check_all_healthy(self):
        """测试全部健康"""
        checker = HealthChecker()

        checker.register_check("test1", lambda: HealthStatus(
            name="test1", status="healthy"
        ))
        checker.register_check("test2", lambda: HealthStatus(
            name="test2", status="healthy"
        ))

        result = checker.check_all()
        assert result["status"] == "healthy"
        assert len(result["checks"]) == 2

    def test_check_all_unhealthy(self):
        """测试有不健康的检查"""
        checker = HealthChecker()

        checker.register_check("healthy", lambda: HealthStatus(
            name="healthy", status="healthy"
        ))
        checker.register_check("unhealthy", lambda: HealthStatus(
            name="unhealthy", status="unhealthy", message="Error"
        ))

        result = checker.check_all()
        assert result["status"] == "unhealthy"

    def test_check_exception(self):
        """测试检查异常"""
        checker = HealthChecker()

        def failing_check():
            raise Exception("Test error")

        checker.register_check("failing", failing_check)
        result = checker.check_all()

        assert result["status"] == "unhealthy"
        assert any(c["name"] == "failing" for c in result["checks"])

    def test_get_system_metrics(self):
        """测试获取系统指标"""
        checker = HealthChecker()
        metrics = checker.get_system_metrics()

        assert "cpu" in metrics or "error" in metrics

    def test_singleton(self):
        """测试单例模式"""
        checker1 = get_health_checker()
        checker2 = get_health_checker()
        assert checker1 is checker2
