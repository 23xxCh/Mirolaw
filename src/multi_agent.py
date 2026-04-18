"""
多智能体预测架构模块

参考MiroFish实现多智能体协作预测，包含：
- DataCollectorAgent: 数据采集智能体
- RiskAnalyzerAgent: 风险分析智能体
- LawMatcherAgent: 法律匹配智能体
- SuggestionAgent: 建议生成智能体
- CoordinatorAgent: 协调智能体
"""

import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """智能体角色"""
    COORDINATOR = "coordinator"
    DATA_COLLECTOR = "data_collector"
    RISK_ANALYZER = "risk_analyzer"
    LAW_MATCHER = "law_matcher"
    SUGGESTION_GENERATOR = "suggestion_generator"


@dataclass
class AgentMessage:
    """智能体消息"""
    from_agent: str
    to_agent: str
    content: Dict
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AgentResult:
    """智能体执行结果"""
    agent_name: str
    success: bool
    data: Dict
    errors: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class BaseAgent:
    """基础智能体"""

    def __init__(self, name: str, role: AgentRole):
        self.name = name
        self.role = role
        self.memory: List[Dict] = []
        self.status = "idle"

    def receive(self, message: AgentMessage) -> None:
        """接收消息"""
        self.memory.append({
            "from": message.from_agent,
            "content": message.content,
            "timestamp": message.timestamp
        })
        logger.debug(f"[{self.name}] Received message from {message.from_agent}")

    def send(self, to_agent: str, content: Dict) -> AgentMessage:
        """发送消息"""
        return AgentMessage(
            from_agent=self.name,
            to_agent=to_agent,
            content=content
        )

    def execute(self, context: Dict) -> AgentResult:
        """执行任务"""
        raise NotImplementedError


class DataCollectorAgent(BaseAgent):
    """数据采集智能体"""

    def __init__(self):
        super().__init__("DataCollector", AgentRole.DATA_COLLECTOR)

    def execute(self, context: Dict) -> AgentResult:
        """采集和预处理数据"""
        self.status = "working"
        platform_data = context.get("platform_data", {})

        try:
            # 数据标准化
            processed_data = {
                "product_info": platform_data.get("product_info", {}),
                "marketing_content": self._normalize_marketing(
                    platform_data.get("marketing_content", [])
                ),
                "company_info": {
                    "size": platform_data.get("company_size", "中型"),
                    "revenue": platform_data.get("annual_revenue", 0)
                },
                "metadata": {
                    "collected_at": datetime.now().isoformat(),
                    "data_completeness": self._calculate_completeness(platform_data)
                }
            }

            self.status = "completed"
            return AgentResult(
                agent_name=self.name,
                success=True,
                data={"processed_data": processed_data}
            )

        except Exception as e:
            self.status = "failed"
            return AgentResult(
                agent_name=self.name,
                success=False,
                data={},
                errors=[str(e)]
            )

    def _normalize_marketing(self, content: List) -> List[str]:
        """标准化营销内容"""
        normalized = []
        for item in content:
            if isinstance(item, dict):
                normalized.append(item.get("text", ""))
            else:
                normalized.append(str(item))
        return normalized

    def _calculate_completeness(self, data: Dict) -> float:
        """计算数据完整度"""
        required_fields = ["product_info", "marketing_content"]
        optional_fields = ["sales_data", "customer_feedback", "company_size"]

        score = 0
        for field in required_fields:
            if data.get(field):
                score += 0.4
        for field in optional_fields:
            if data.get(field):
                score += 0.1

        return min(1.0, score)


class RiskAnalyzerAgent(BaseAgent):
    """风险分析智能体"""

    def __init__(self, predictor):
        super().__init__("RiskAnalyzer", AgentRole.RISK_ANALYZER)
        self.predictor = predictor

    def execute(self, context: Dict) -> AgentResult:
        """分析风险"""
        self.status = "working"
        processed_data = context.get("processed_data", {})

        try:
            # 执行风险预测
            prediction = self.predictor.predict(processed_data)

            # 提取高风险项
            high_risks = [
                r for r in prediction.get("risk_assessments", [])
                if r.get("probability", 0) >= 0.5
            ]

            self.status = "completed"
            return AgentResult(
                agent_name=self.name,
                success=True,
                data={
                    "prediction": prediction,
                    "high_risks": high_risks,
                    "risk_count": len(prediction.get("risk_assessments", []))
                }
            )

        except Exception as e:
            self.status = "failed"
            return AgentResult(
                agent_name=self.name,
                success=False,
                data={},
                errors=[str(e)]
            )


class LawMatcherAgent(BaseAgent):
    """法律匹配智能体"""

    def __init__(self, law_database):
        super().__init__("LawMatcher", AgentRole.LAW_MATCHER)
        self.law_database = law_database

    def execute(self, context: Dict) -> AgentResult:
        """匹配相关法律"""
        self.status = "working"
        high_risks = context.get("high_risks", [])

        try:
            law_matches = {}

            for risk in high_risks:
                risk_type = risk.get("risk_type")
                articles = self.law_database.get_articles_by_risk_type(risk_type)
                law_matches[risk_type] = articles

            self.status = "completed"
            return AgentResult(
                agent_name=self.name,
                success=True,
                data={
                    "law_matches": law_matches,
                    "total_articles": sum(len(v) for v in law_matches.values())
                }
            )

        except Exception as e:
            self.status = "failed"
            return AgentResult(
                agent_name=self.name,
                success=False,
                data={},
                errors=[str(e)]
            )


class SuggestionAgent(BaseAgent):
    """建议生成智能体"""

    def __init__(self, suggestion_generator):
        super().__init__("SuggestionGenerator", AgentRole.SUGGESTION_GENERATOR)
        self.generator = suggestion_generator

    def execute(self, context: Dict) -> AgentResult:
        """生成建议"""
        self.status = "working"
        high_risks = context.get("high_risks", [])
        law_matches = context.get("law_matches", {})

        try:
            suggestions = {}

            for risk in high_risks:
                risk_type = risk.get("risk_type")
                result = self.generator.generate_suggestions(
                    risk_type=risk_type,
                    simulation_result=risk,
                    similar_cases=[]
                )
                suggestions[risk_type] = result

            self.status = "completed"
            return AgentResult(
                agent_name=self.name,
                success=True,
                data={
                    "suggestions": suggestions,
                    "suggestion_count": len(suggestions)
                }
            )

        except Exception as e:
            self.status = "failed"
            return AgentResult(
                agent_name=self.name,
                success=False,
                data={},
                errors=[str(e)]
            )


class CoordinatorAgent(BaseAgent):
    """协调智能体"""

    def __init__(self, agents: Dict[str, BaseAgent]):
        super().__init__("Coordinator", AgentRole.COORDINATOR)
        self.agents = agents

    def execute(self, context: Dict) -> AgentResult:
        """协调所有智能体执行"""
        self.status = "working"
        results = {}
        errors = []

        try:
            # 1. 数据采集
            data_collector = self.agents.get("data_collector")
            if data_collector:
                result = data_collector.execute(context)
                results["data_collection"] = result.data
                if not result.success:
                    errors.extend(result.errors)
                context.update(result.data)

            # 2. 风险分析
            risk_analyzer = self.agents.get("risk_analyzer")
            if risk_analyzer:
                result = risk_analyzer.execute(context)
                results["risk_analysis"] = result.data
                if not result.success:
                    errors.extend(result.errors)
                context.update(result.data)

            # 3. 法律匹配
            law_matcher = self.agents.get("law_matcher")
            if law_matcher:
                result = law_matcher.execute(context)
                results["law_matching"] = result.data
                if not result.success:
                    errors.extend(result.errors)
                context.update(result.data)

            # 4. 建议生成
            suggestion_agent = self.agents.get("suggestion_generator")
            if suggestion_agent:
                result = suggestion_agent.execute(context)
                results["suggestion_generation"] = result.data
                if not result.success:
                    errors.extend(result.errors)

            self.status = "completed"
            return AgentResult(
                agent_name=self.name,
                success=len(errors) == 0,
                data={
                    "results": results,
                    "final_report": self._generate_report(results)
                },
                errors=errors
            )

        except Exception as e:
            self.status = "failed"
            return AgentResult(
                agent_name=self.name,
                success=False,
                data={},
                errors=[str(e)]
            )

    def _generate_report(self, results: Dict) -> Dict:
        """生成最终报告"""
        prediction = results.get("risk_analysis", {}).get("prediction", {})
        law_matches = results.get("law_matching", {}).get("law_matches", {})
        suggestions = results.get("suggestion_generation", {}).get("suggestions", {})

        return {
            "summary": {
                "overall_risk_score": prediction.get("overall_risk_score", 0),
                "high_risk_count": len(results.get("risk_analysis", {}).get("high_risks", [])),
                "matched_laws": sum(len(v) for v in law_matches.values()),
                "suggestions_generated": len(suggestions)
            },
            "risk_assessments": prediction.get("risk_assessments", []),
            "law_matches": law_matches,
            "suggestions": suggestions,
            "generated_at": datetime.now().isoformat()
        }


class MultiAgentSystem:
    """多智能体系统"""

    def __init__(self, predictor=None, law_database=None, suggestion_generator=None):
        """初始化多智能体系统"""
        from .predictor import RiskPredictor
        from .law_database import get_law_database
        from .suggestion_generator import SuggestionGenerator

        self.predictor = predictor or RiskPredictor(config={})
        self.law_database = law_database or get_law_database()
        self.suggestion_generator = suggestion_generator or SuggestionGenerator()

        # 创建智能体
        self.agents = {
            "data_collector": DataCollectorAgent(),
            "risk_analyzer": RiskAnalyzerAgent(self.predictor),
            "law_matcher": LawMatcherAgent(self.law_database),
            "suggestion_generator": SuggestionAgent(self.suggestion_generator)
        }

        # 创建协调器
        self.coordinator = CoordinatorAgent(self.agents)

        logger.info("Multi-Agent System initialized with 4 agents")

    def predict(self, platform_data: Dict) -> Dict:
        """执行多智能体预测"""
        context = {"platform_data": platform_data}

        result = self.coordinator.execute(context)

        if result.success:
            return result.data.get("final_report", {})
        else:
            return {
                "error": "Multi-agent prediction failed",
                "details": result.errors
            }

    def get_agent_status(self) -> Dict:
        """获取所有智能体状态"""
        return {
            name: {
                "role": agent.role.value,
                "status": agent.status,
                "memory_size": len(agent.memory)
            }
            for name, agent in self.agents.items()
        }


# 全局实例
_multi_agent_system = None


def get_multi_agent_system() -> MultiAgentSystem:
    """获取多智能体系统实例"""
    global _multi_agent_system
    if _multi_agent_system is None:
        _multi_agent_system = MultiAgentSystem()
    return _multi_agent_system
