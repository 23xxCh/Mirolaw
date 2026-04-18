"""
健康检查与监控模块

提供系统健康状态检查和监控指标。
"""

import time
import psutil
from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class HealthStatus:
    """健康状态"""
    name: str
    status: str  # healthy, unhealthy, degraded
    message: str = ""
    details: Dict = field(default_factory=dict)


class HealthChecker:
    """健康检查器"""

    def __init__(self):
        self.checks: Dict[str, callable] = {}
        self._start_time = time.time()

    def register_check(self, name: str, check_func: callable):
        """注册健康检查"""
        self.checks[name] = check_func

    def check_all(self) -> Dict[str, Any]:
        """执行所有健康检查"""
        results = []
        all_healthy = True

        for name, check_func in self.checks.items():
            try:
                status = check_func()
                results.append(status)
                if status.status != "healthy":
                    all_healthy = False
            except Exception as e:
                results.append(HealthStatus(
                    name=name,
                    status="unhealthy",
                    message=str(e)
                ))
                all_healthy = False

        return {
            "status": "healthy" if all_healthy else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": int(time.time() - self._start_time),
            "checks": [
                {
                    "name": r.name,
                    "status": r.status,
                    "message": r.message,
                    "details": r.details
                }
                for r in results
            ]
        }

    def get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count()
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent
                },
                "uptime_seconds": int(time.time() - self._start_time)
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {"error": str(e)}


# 默认健康检查函数
def check_api_health() -> HealthStatus:
    """检查API健康"""
    return HealthStatus(
        name="api",
        status="healthy",
        message="API is running"
    )


def check_predictor_health() -> HealthStatus:
    """检查预测器健康"""
    try:
        from .predictor import get_risk_predictor
        predictor = get_risk_predictor()
        return HealthStatus(
            name="predictor",
            status="healthy",
            message="Risk predictor is ready",
            details={"risk_types": len(predictor.risk_types)}
        )
    except Exception as e:
        return HealthStatus(
            name="predictor",
            status="unhealthy",
            message=str(e)
        )


def check_knowledge_graph_health() -> HealthStatus:
    """检查知识图谱健康"""
    try:
        from .knowledge_graph import get_knowledge_graph
        kg = get_knowledge_graph()
        cases = kg.get_all_cases()
        return HealthStatus(
            name="knowledge_graph",
            status="healthy",
            message="Knowledge graph is ready",
            details={"cases_count": len(cases)}
        )
    except Exception as e:
        return HealthStatus(
            name="knowledge_graph",
            status="unhealthy",
            message=str(e)
        )


def check_law_database_health() -> HealthStatus:
    """检查法律数据库健康"""
    try:
        from .law_database import get_law_database
        db = get_law_database()
        stats = db.get_statistics()
        return HealthStatus(
            name="law_database",
            status="healthy",
            message="Law database is ready",
            details=stats
        )
    except Exception as e:
        return HealthStatus(
            name="law_database",
            status="unhealthy",
            message=str(e)
        )


def check_cache_health() -> HealthStatus:
    """检查缓存健康"""
    try:
        from .cache import get_global_cache
        cache = get_global_cache()
        stats = cache.get_stats()
        return HealthStatus(
            name="cache",
            status="healthy",
            message="Cache is ready",
            details=stats
        )
    except Exception as e:
        return HealthStatus(
            name="cache",
            status="unhealthy",
            message=str(e)
        )


def check_alert_system_health() -> HealthStatus:
    """检查预警系统健康"""
    try:
        from .alert_system import get_alert_manager
        manager = get_alert_manager()
        stats = manager.get_alert_stats()
        return HealthStatus(
            name="alert_system",
            status="healthy",
            message="Alert system is ready",
            details=stats
        )
    except Exception as e:
        return HealthStatus(
            name="alert_system",
            status="unhealthy",
            message=str(e)
        )


# 全局健康检查器
_health_checker = None


def get_health_checker() -> HealthChecker:
    """获取健康检查器实例"""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()

        # 注册默认检查
        _health_checker.register_check("api", check_api_health)
        _health_checker.register_check("predictor", check_predictor_health)
        _health_checker.register_check("knowledge_graph", check_knowledge_graph_health)
        _health_checker.register_check("law_database", check_law_database_health)
        _health_checker.register_check("cache", check_cache_health)
        _health_checker.register_check("alert_system", check_alert_system_health)

    return _health_checker
