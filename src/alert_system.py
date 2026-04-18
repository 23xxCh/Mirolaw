"""
实时预警系统模块

提供WebSocket实时推送、主动预警、预警规则引擎等功能。
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Set, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """预警级别"""
    INFO = "info"
    WARNING = "warning"
    DANGER = "danger"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """预警状态"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


@dataclass
class Alert:
    """预警信息"""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    message: str = ""
    level: AlertLevel = AlertLevel.WARNING
    status: AlertStatus = AlertStatus.ACTIVE
    risk_type: str = ""
    probability: float = 0.0
    source: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)


@dataclass
class AlertRule:
    """预警规则"""
    rule_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    risk_types: List[str] = field(default_factory=list)
    probability_threshold: float = 0.5
    level: AlertLevel = AlertLevel.WARNING
    enabled: bool = True
    actions: List[str] = field(default_factory=list)  # 通知动作
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class WebSocketManager:
    """WebSocket连接管理器"""

    def __init__(self):
        self.connections: Set[Any] = set()
        self.subscriptions: Dict[str, Set[Any]] = {}  # topic -> connections

    async def connect(self, websocket: Any):
        """添加连接"""
        self.connections.add(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.connections)}")

    async def disconnect(self, websocket: Any):
        """移除连接"""
        self.connections.discard(websocket)
        # 从所有订阅中移除
        for topic in self.subscriptions:
            self.subscriptions[topic].discard(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.connections)}")

    async def subscribe(self, websocket: Any, topic: str):
        """订阅主题"""
        if topic not in self.subscriptions:
            self.subscriptions[topic] = set()
        self.subscriptions[topic].add(websocket)
        logger.info(f"Subscribed to {topic}")

    async def unsubscribe(self, websocket: Any, topic: str):
        """取消订阅"""
        if topic in self.subscriptions:
            self.subscriptions[topic].discard(websocket)

    async def broadcast(self, message: Dict):
        """广播消息到所有连接"""
        message_json = json.dumps(message, ensure_ascii=False)
        disconnected = set()

        for connection in self.connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Send failed: {e}")
                disconnected.add(connection)

        # 清理断开的连接
        for conn in disconnected:
            self.connections.discard(conn)

    async def publish(self, topic: str, message: Dict):
        """发布消息到特定主题"""
        if topic not in self.subscriptions:
            return

        message_json = json.dumps({
            "topic": topic,
            "data": message,
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False)

        disconnected = set()
        for connection in self.subscriptions[topic]:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Publish failed: {e}")
                disconnected.add(connection)

        for conn in disconnected:
            self.subscriptions[topic].discard(conn)

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "total_connections": len(self.connections),
            "topics": list(self.subscriptions.keys()),
            "subscriptions": {k: len(v) for k, v in self.subscriptions.items()}
        }


class AlertRuleEngine:
    """预警规则引擎"""

    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self._load_default_rules()

    def _load_default_rules(self):
        """加载默认规则"""
        default_rules = [
            AlertRule(
                name="高风险预警",
                description="风险概率超过70%时触发高风险预警",
                risk_types=["虚假宣传", "价格欺诈", "知识产权侵权"],
                probability_threshold=0.7,
                level=AlertLevel.DANGER,
                actions=["websocket", "log"]
            ),
            AlertRule(
                name="中等风险预警",
                description="风险概率超过50%时触发中等风险预警",
                risk_types=["虚假宣传", "价格欺诈", "知识产权侵权", "产品质量问题"],
                probability_threshold=0.5,
                level=AlertLevel.WARNING,
                actions=["websocket"]
            ),
            AlertRule(
                name="个人信息泄露预警",
                description="涉及个人信息泄露风险时立即预警",
                risk_types=["个人信息泄露"],
                probability_threshold=0.3,
                level=AlertLevel.CRITICAL,
                actions=["websocket", "log"]
            ),
            AlertRule(
                name="不正当竞争预警",
                description="检测到刷单刷评等不正当竞争行为",
                risk_types=["不正当竞争"],
                probability_threshold=0.4,
                level=AlertLevel.WARNING,
                actions=["websocket"]
            )
        ]

        for rule in default_rules:
            self.rules[rule.rule_id] = rule

    def add_rule(self, rule: AlertRule) -> str:
        """添加规则"""
        self.rules[rule.rule_id] = rule
        logger.info(f"Added rule: {rule.name}")
        return rule.rule_id

    def remove_rule(self, rule_id: str) -> bool:
        """移除规则"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            return True
        return False

    def evaluate(self, risk_type: str, probability: float) -> List[Alert]:
        """评估风险并生成预警"""
        alerts = []

        for rule_id, rule in self.rules.items():
            if not rule.enabled:
                continue

            # 检查风险类型是否匹配
            if rule.risk_types and risk_type not in rule.risk_types:
                continue

            # 检查概率是否超过阈值
            if probability >= rule.probability_threshold:
                alert = Alert(
                    title=f"{rule.name}",
                    message=f"检测到{risk_type}风险，概率: {probability:.1%}，超过阈值: {rule.probability_threshold:.1%}",
                    level=rule.level,
                    risk_type=risk_type,
                    probability=probability,
                    source="rule_engine",
                    metadata={"rule_id": rule_id, "actions": rule.actions}
                )
                alerts.append(alert)

        return alerts

    def get_rules(self) -> List[Dict]:
        """获取所有规则"""
        return [
            {
                "rule_id": r.rule_id,
                "name": r.name,
                "description": r.description,
                "risk_types": r.risk_types,
                "probability_threshold": r.probability_threshold,
                "level": r.level.value,
                "enabled": r.enabled,
                "actions": r.actions
            }
            for r in self.rules.values()
        ]


class AlertManager:
    """预警管理器"""

    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.ws_manager = WebSocketManager()
        self.rule_engine = AlertRuleEngine()
        self.notification_handlers: Dict[str, Callable] = {}

    def register_notification_handler(self, channel: str, handler: Callable):
        """注册通知处理器"""
        self.notification_handlers[channel] = handler
        logger.info(f"Registered notification handler: {channel}")

    async def create_alert(self, alert: Alert) -> str:
        """创建预警"""
        self.alerts[alert.alert_id] = alert

        # 发送WebSocket通知
        await self.ws_manager.publish("alerts", {
            "type": "new_alert",
            "alert": {
                "alert_id": alert.alert_id,
                "title": alert.title,
                "message": alert.message,
                "level": alert.level.value,
                "risk_type": alert.risk_type,
                "probability": alert.probability,
                "created_at": alert.created_at
            }
        })

        # 执行通知动作
        actions = alert.metadata.get("actions", [])
        await self._execute_actions(alert, actions)

        logger.info(f"Created alert: {alert.alert_id} - {alert.title}")
        return alert.alert_id

    async def _execute_actions(self, alert: Alert, actions: List[str]):
        """执行通知动作"""
        for action in actions:
            if action == "log":
                logger.warning(f"[ALERT] {alert.level.value.upper()}: {alert.message}")
            elif action in self.notification_handlers:
                try:
                    await self.notification_handlers[action](alert)
                except Exception as e:
                    logger.error(f"Action {action} failed: {e}")

    async def process_risk_result(self, risk_result: Dict):
        """处理风险预测结果，触发预警"""
        risk_assessments = risk_result.get("risk_assessments", [])

        for assessment in risk_assessments:
            risk_type = assessment.get("risk_type")
            probability = assessment.get("probability", 0)

            # 评估规则
            alerts = self.rule_engine.evaluate(risk_type, probability)

            for alert in alerts:
                await self.create_alert(alert)

    def acknowledge_alert(self, alert_id: str) -> bool:
        """确认预警"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.updated_at = datetime.now().isoformat()
            return True
        return False

    def resolve_alert(self, alert_id: str) -> bool:
        """解决预警"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.updated_at = datetime.now().isoformat()
            return True
        return False

    def get_active_alerts(self) -> List[Dict]:
        """获取活跃预警"""
        return [
            {
                "alert_id": a.alert_id,
                "title": a.title,
                "message": a.message,
                "level": a.level.value,
                "status": a.status.value,
                "risk_type": a.risk_type,
                "probability": a.probability,
                "created_at": a.created_at
            }
            for a in self.alerts.values()
            if a.status == AlertStatus.ACTIVE
        ]

    def get_alert_stats(self) -> Dict:
        """获取预警统计"""
        total = len(self.alerts)
        by_level = {}
        by_status = {}

        for alert in self.alerts.values():
            level = alert.level.value
            status = alert.status.value
            by_level[level] = by_level.get(level, 0) + 1
            by_status[status] = by_status.get(status, 0) + 1

        return {
            "total": total,
            "active": by_status.get("active", 0),
            "by_level": by_level,
            "by_status": by_status
        }


class ProactiveMonitor:
    """主动监控器"""

    def __init__(self, alert_manager: AlertManager, check_interval: int = 300):
        self.alert_manager = alert_manager
        self.check_interval = check_interval  # 秒
        self.running = False
        self.monitored_items: Dict[str, Dict] = {}  # item_id -> config
        self._task = None

    def add_monitored_item(self, item_id: str, config: Dict):
        """添加监控项"""
        self.monitored_items[item_id] = {
            "config": config,
            "last_check": None,
            "check_count": 0
        }
        logger.info(f"Added monitored item: {item_id}")

    def remove_monitored_item(self, item_id: str):
        """移除监控项"""
        self.monitored_items.pop(item_id, None)

    async def start(self):
        """启动监控"""
        self.running = True
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info("Proactive monitor started")

    async def stop(self):
        """停止监控"""
        self.running = False
        if self._task:
            self._task.cancel()
        logger.info("Proactive monitor stopped")

    async def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                await self._check_all_items()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
                await asyncio.sleep(60)

    async def _check_all_items(self):
        """检查所有监控项"""
        from .predictor import RiskPredictor

        predictor = RiskPredictor(config={})

        for item_id, item_data in self.monitored_items.items():
            try:
                config = item_data["config"]
                platform_data = config.get("platform_data", {})

                # 执行预测
                result = predictor.predict(platform_data)

                # 处理结果，触发预警
                await self.alert_manager.process_risk_result(result)

                # 更新状态
                item_data["last_check"] = datetime.now().isoformat()
                item_data["check_count"] += 1

            except Exception as e:
                logger.error(f"Check failed for {item_id}: {e}")

    def get_status(self) -> Dict:
        """获取监控状态"""
        return {
            "running": self.running,
            "check_interval": self.check_interval,
            "monitored_items": len(self.monitored_items),
            "items": [
                {
                    "item_id": k,
                    "last_check": v["last_check"],
                    "check_count": v["check_count"]
                }
                for k, v in self.monitored_items.items()
            ]
        }


# 全局实例
_alert_manager = None
_proactive_monitor = None


def get_alert_manager() -> AlertManager:
    """获取预警管理器"""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager


def get_proactive_monitor() -> ProactiveMonitor:
    """获取主动监控器"""
    global _proactive_monitor
    if _proactive_monitor is None:
        _proactive_monitor = ProactiveMonitor(get_alert_manager())
    return _proactive_monitor
