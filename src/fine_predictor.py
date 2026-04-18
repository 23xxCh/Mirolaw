"""
罚款预测模块

本模块负责预测电商平台违规行为可能面临的罚款金额范围，
基于历史案例和风险概率进行综合分析。
"""

from typing import Dict, List, Optional
import logging
from datetime import datetime
import statistics

logger = logging.getLogger(__name__)


class FinePredictor:
    """
    罚款预测器

    基于法律知识图谱和历史处罚案例，预测违规行为可能面临的罚款金额。
    """

    # 企业规模系数
    COMPANY_SIZE_MULTIPLIER = {
        "大型": 1.5,
        "中型": 1.0,
        "小型": 0.6,
        "微型": 0.3
    }

    # 违规严重程度系数
    SEVERITY_MULTIPLIER = {
        "严重": 1.5,
        "较重": 1.2,
        "一般": 1.0,
        "轻微": 0.5
    }

    def __init__(self, knowledge_graph) -> None:
        """初始化罚款预测器"""
        if knowledge_graph is None:
            raise ValueError("knowledge_graph cannot be None")

        self.knowledge_graph = knowledge_graph
        self.historical_cache = {}
        logger.info("FinePredictor initialized successfully")

    def predict_fine(
        self,
        risk_type: str,
        platform_data: Dict,
        simulation_result: Dict
    ) -> Dict:
        """预测罚款金额范围"""
        # 查询历史案例
        historical_cases = self._query_historical_cases(risk_type)

        # 获取法律依据
        legal_basis = self.knowledge_graph.get_legal_basis(risk_type)

        # 计算罚款范围
        probability = simulation_result.get("probability", 0.5)
        fine_range = self._calculate_fine_range(
            historical_cases,
            probability,
            platform_data
        )

        # 分析影响因素
        factors = self._analyze_factors(platform_data, risk_type)

        # 计算置信度
        confidence = self._calculate_confidence(historical_cases)

        result = {
            "fine_range": fine_range,
            "confidence": round(confidence, 3),
            "legal_basis": legal_basis,
            "historical_cases": historical_cases[:5],
            "factors": factors,
            "timestamp": datetime.now().isoformat(),
            "risk_type": risk_type,
            "probability": probability
        }

        logger.info(f"Fine prediction completed for {risk_type}")
        return result

    def _query_historical_cases(self, risk_type: str) -> List:
        """查询历史处罚案例"""
        if risk_type in self.historical_cache:
            logger.info(f"Retrieved {risk_type} cases from cache")
            return self.historical_cache[risk_type]

        try:
            cases = self.knowledge_graph.query_similar_cases(risk_type)
            self.historical_cache[risk_type] = cases
            logger.info(f"Queried {len(cases)} historical cases for {risk_type}")
            return cases
        except Exception as e:
            logger.error(f"Failed to query historical cases: {e}")
            return []

    def _calculate_fine_range(
        self,
        historical_cases: List,
        probability: float,
        platform_data: Dict
    ) -> Dict:
        """计算罚款金额范围"""
        if not historical_cases:
            # 无历史案例时使用默认值
            return self._calculate_default_fine(platform_data, probability)

        # 提取历史罚款金额
        fine_amounts = [
            case.get("fine_amount", 0)
            for case in historical_cases
            if case.get("fine_amount", 0) > 0
        ]

        if not fine_amounts:
            return self._calculate_default_fine(platform_data, probability)

        # 基础统计
        min_fine = min(fine_amounts)
        max_fine = max(fine_amounts)
        avg_fine = statistics.mean(fine_amounts)

        # 根据企业规模调整
        company_size = platform_data.get("company_size", "中型")
        size_multiplier = self.COMPANY_SIZE_MULTIPLIER.get(company_size, 1.0)

        # 根据严重程度调整
        severity = platform_data.get("violation_severity", "一般")
        severity_multiplier = self.SEVERITY_MULTIPLIER.get(severity, 1.0)

        # 根据概率调整
        probability_multiplier = 0.5 + probability * 0.5

        # 计算最终范围
        total_multiplier = size_multiplier * severity_multiplier * probability_multiplier

        adjusted_min = round(min_fine * total_multiplier, 2)
        adjusted_max = round(max_fine * total_multiplier, 2)
        expected_fine = round(avg_fine * total_multiplier, 2)

        return {
            "min": adjusted_min,
            "max": adjusted_max,
            "expected": expected_fine,
            "currency": "CNY"
        }

    def _calculate_default_fine(self, platform_data: Dict, probability: float) -> Dict:
        """计算默认罚款范围（无历史案例时）"""
        # 基础罚款范围
        base_min = 50000
        base_max = 500000

        # 根据企业规模调整
        company_size = platform_data.get("company_size", "中型")
        size_multiplier = self.COMPANY_SIZE_MULTIPLIER.get(company_size, 1.0)

        # 根据营业额调整
        annual_revenue = platform_data.get("annual_revenue", 0)
        if annual_revenue > 10000000:  # 1000万以上
            revenue_multiplier = 1.5
        elif annual_revenue > 1000000:  # 100万以上
            revenue_multiplier = 1.0
        else:
            revenue_multiplier = 0.5

        # 根据概率调整
        probability_multiplier = 0.5 + probability * 0.5

        total_multiplier = size_multiplier * revenue_multiplier * probability_multiplier

        return {
            "min": round(base_min * total_multiplier, 2),
            "max": round(base_max * total_multiplier, 2),
            "expected": round((base_min + base_max) / 2 * total_multiplier, 2),
            "currency": "CNY"
        }

    def _analyze_factors(self, platform_data: Dict, risk_type: str) -> Dict:
        """分析影响罚款的因素"""
        company_size = platform_data.get("company_size", "中型")
        violation_history = platform_data.get("violation_history", [])
        severity = platform_data.get("violation_severity", "一般")

        # 企业规模影响
        if company_size in ["大型", "中型"]:
            size_impact = "罚款金额可能较高"
        else:
            size_impact = "罚款金额可能较低"

        # 违规历史影响
        if len(violation_history) > 2:
            history_impact = "多次违规，罚款可能加重"
        elif len(violation_history) > 0:
            history_impact = "有违规记录，需注意"
        else:
            history_impact = "无违规记录"

        # 严重程度影响
        if severity in ["严重", "较重"]:
            severity_impact = "情节严重，罚款可能加重"
        else:
            severity_impact = "情节一般"

        # 缓解潜力
        mitigation_potential = "高" if severity in ["轻微", "一般"] else "中"

        return {
            "company_size_impact": size_impact,
            "violation_history_impact": history_impact,
            "severity_impact": severity_impact,
            "mitigation_potential": mitigation_potential,
            "factors_count": {
                "violation_history_count": len(violation_history),
                "company_size": company_size,
                "severity": severity
            }
        }

    def _calculate_confidence(self, historical_cases: List) -> float:
        """计算预测置信度"""
        if not historical_cases:
            return 0.5

        # 基于案例数量计算置信度
        case_count = len(historical_cases)
        base_confidence = min(0.9, 0.5 + case_count * 0.05)

        return base_confidence

    def update_cache(self, risk_type: str, cases: List) -> None:
        """更新历史案例缓存"""
        self.historical_cache[risk_type] = cases
        logger.info(f"Updated cache for {risk_type}")

    def get_fine_statistics(self, risk_type: str) -> Dict:
        """获取罚款统计信息"""
        cases = self._query_historical_cases(risk_type)

        if not cases:
            return {"count": 0, "avg": 0, "min": 0, "max": 0}

        fine_amounts = [
            case.get("fine_amount", 0)
            for case in cases
            if case.get("fine_amount", 0) > 0
        ]

        if not fine_amounts:
            return {"count": len(cases), "avg": 0, "min": 0, "max": 0}

        return {
            "count": len(fine_amounts),
            "avg": round(statistics.mean(fine_amounts), 2),
            "min": min(fine_amounts),
            "max": max(fine_amounts),
            "median": round(statistics.median(fine_amounts), 2) if len(fine_amounts) > 1 else fine_amounts[0]
        }
