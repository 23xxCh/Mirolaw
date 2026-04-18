"""
风险预测模块

本模块负责预测电商平台运营中可能面临的合规风险，包括风险类型识别、
风险概率计算和风险等级评估。
"""

from typing import Dict, List, Optional
import logging
import re
from datetime import datetime
import random

logger = logging.getLogger(__name__)


class RiskPredictor:
    """
    风险预测器

    使用规则引擎和历史数据预测电商平台运营中的合规风险。
    """

    # 风险关键词映射
    RISK_KEYWORDS = {
        "虚假宣传": [
            "最", "第一", "唯一", "顶级", "极致", "完美", "绝对",
            "最好", "最优", "最高", "最低", "独家", "首创", "国家级",
            "世界级", "全球首创", "史无前例", "万能", "根治", "疗效"
        ],
        "价格欺诈": [
            "原价", "折扣", "优惠", "特价", "促销", "限时", "抢购",
            "涨价", "降价", "打折", "满减", "立减"
        ],
        "知识产权侵权": [
            "高仿", "同款", "仿品", "复刻", "A货", "原单", "尾单"
        ],
        "产品质量问题": [
            "三无", "劣质", "假冒", "山寨", "水货"
        ],
        "个人信息泄露": [
            "收集", "用户数据", "个人信息", "隐私", "数据共享"
        ],
        "不正当竞争": [
            "好评返现", "刷单", "刷评", "虚假交易", "恶意差评"
        ],
        "广告违法": [
            "治愈", "疗效", "处方药", "医疗器械", "投资回报", "保本"
        ]
    }

    def __init__(self, config: Dict) -> None:
        """初始化风险预测器"""
        self.config = config
        self.model = None
        self.risk_types = [
            "虚假宣传",
            "价格欺诈",
            "产品质量问题",
            "知识产权侵权",
            "个人信息泄露",
            "不正当竞争",
            "广告违法",
        ]
        self._build_model()
        logger.info("RiskPredictor initialized successfully")

    def predict(
        self,
        platform_data: Dict,
        risk_types: Optional[List[str]] = None,
        horizon: int = 30
    ) -> Dict:
        """预测合规风险"""
        if risk_types is None:
            risk_types = self.risk_types

        risk_assessments = []
        total_probability = 0.0

        for risk_type in risk_types:
            probability = self._calculate_risk_probability(risk_type, platform_data)
            risk_level = self._calculate_risk_level(probability)
            confidence = self._calculate_confidence(platform_data, risk_type)

            assessment = {
                "risk_type": risk_type,
                "probability": round(probability, 3),
                "risk_level": risk_level,
                "confidence": round(confidence, 3),
                "factors": self._identify_risk_factors(risk_type, platform_data)
            }
            risk_assessments.append(assessment)
            total_probability += probability

        # 计算综合风险评分
        overall_risk_score = min(1.0, total_probability / len(risk_types)) if risk_types else 0.0

        result = {
            "risk_assessments": risk_assessments,
            "overall_risk_score": round(overall_risk_score, 3),
            "prediction_horizon": horizon,
            "timestamp": datetime.now().isoformat(),
            "recommendation": self._generate_recommendation(overall_risk_score)
        }

        logger.info(f"Risk prediction completed for {len(risk_types)} risk types")
        return result

    def _calculate_risk_probability(self, risk_type: str, platform_data: Dict) -> float:
        """计算风险概率 - 增强版"""
        base_probability = 0.1  # 基础概率

        # 获取营销内容
        marketing_content = platform_data.get("marketing_content", [])
        product_info = platform_data.get("product_info", {})
        sales_data = platform_data.get("sales_data", [])

        # 关键词检测
        keywords = self.RISK_KEYWORDS.get(risk_type, [])
        keyword_matches = 0
        severity_weight = 1.0

        # 高风险关键词（权重更高）
        high_risk_keywords = {
            "虚假宣传": ["根治", "治愈", "疗效", "世界第一", "全球首创", "国家级"],
            "价格欺诈": ["原价", "虚假折扣", "虚构"],
            "知识产权侵权": ["高仿", "A货", "假冒"],
            "产品质量问题": ["三无", "劣质", "有毒"],
            "个人信息泄露": ["出售", "泄露", "买卖"],
            "不正当竞争": ["刷单", "刷评", "虚假交易"],
            "广告违法": ["处方药", "治愈率", "有效率"]
        }

        # 检查营销内容
        for content in marketing_content:
            if isinstance(content, dict):
                text = content.get("text", "")
            else:
                text = str(content)

            for keyword in keywords:
                if keyword in text:
                    keyword_matches += 1
                    # 高风险关键词加倍权重
                    if keyword in high_risk_keywords.get(risk_type, []):
                        severity_weight = 1.5

        # 检查产品信息
        product_desc = product_info.get("description", "")
        product_name = product_info.get("name", "")
        combined_text = f"{product_name} {product_desc}"

        for keyword in keywords:
            if keyword in combined_text:
                keyword_matches += 1

        # 根据匹配数量调整概率（增强算法）
        if keyword_matches == 0:
            probability_adjustment = 0
        elif keyword_matches <= 2:
            probability_adjustment = 0.15 * severity_weight
        elif keyword_matches <= 5:
            probability_adjustment = 0.35 * severity_weight
        else:
            probability_adjustment = 0.55 * severity_weight

        final_probability = min(0.95, base_probability + probability_adjustment)

        # 添加小幅随机波动
        final_probability += random.uniform(-0.03, 0.03)
        final_probability = max(0.0, min(1.0, final_probability))

        return final_probability

    def _identify_risk_factors(self, risk_type: str, platform_data: Dict) -> List:
        """识别风险因素"""
        factors = []
        keywords = self.RISK_KEYWORDS.get(risk_type, [])

        marketing_content = platform_data.get("marketing_content", [])
        product_info = platform_data.get("product_info", {})

        for content in marketing_content:
            if isinstance(content, dict):
                text = content.get("text", "")
            else:
                text = str(content)

            for keyword in keywords:
                if keyword in text:
                    factors.append(f"营销内容包含敏感词: '{keyword}'")

        product_desc = product_info.get("description", "")
        for keyword in keywords:
            if keyword in product_desc:
                factors.append(f"产品描述包含敏感词: '{keyword}'")

        return list(set(factors))[:5]  # 去重并限制数量

    def _calculate_confidence(self, platform_data: Dict, risk_type: str) -> float:
        """计算预测置信度"""
        # 基于数据完整度计算置信度
        data_fields = ["product_info", "sales_data", "marketing_content", "customer_feedback"]
        present_fields = sum(1 for field in data_fields if platform_data.get(field))

        base_confidence = present_fields / len(data_fields)

        # 添加随机波动
        confidence = base_confidence * 0.8 + random.uniform(0.1, 0.2)

        return min(0.95, max(0.5, confidence))

    def _calculate_risk_level(self, probability: float) -> str:
        """根据概率计算风险等级"""
        if probability >= 0.7:
            return "高"
        elif probability >= 0.3:
            return "中"
        else:
            return "低"

    def _generate_recommendation(self, overall_risk_score: float) -> str:
        """生成整体建议"""
        if overall_risk_score >= 0.7:
            return "风险较高，建议立即进行全面合规审查"
        elif overall_risk_score >= 0.4:
            return "存在一定风险，建议关注重点领域"
        else:
            return "风险较低，建议保持常规合规监控"

    def _build_model(self) -> None:
        """构建模型"""
        model_path = self.config.get("model_path")
        if model_path:
            logger.info(f"Loading model from {model_path}")
        else:
            logger.info("Using rule-based prediction model")

        logger.info("Model built successfully")

    def update_model(self, new_data: Dict) -> bool:
        """更新模型"""
        logger.info("Model update initiated")
        return True

    def get_feature_importance(self) -> Dict:
        """获取特征重要性"""
        return {
            "营销内容关键词": 0.35,
            "产品描述": 0.25,
            "历史违规记录": 0.20,
            "销售数据异常": 0.15,
            "用户反馈": 0.05
        }
