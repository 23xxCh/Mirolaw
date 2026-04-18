"""
单元测试 - 风险预测模块
"""

import pytest
from src.predictor import RiskPredictor


class TestRiskPredictor:
    """风险预测器测试"""

    @pytest.fixture
    def predictor(self):
        return RiskPredictor(config={})

    def test_predict_basic(self, predictor):
        """测试基本预测功能"""
        platform_data = {
            "product_info": {"name": "测试产品", "description": "普通产品"},
            "marketing_content": []
        }

        result = predictor.predict(platform_data)

        assert "risk_assessments" in result
        assert "overall_risk_score" in result
        assert "timestamp" in result
        assert len(result["risk_assessments"]) == 7  # 7种风险类型

    def test_predict_high_risk_keywords(self, predictor):
        """测试高风险关键词检测"""
        platform_data = {
            "product_info": {
                "name": "神奇产品",
                "description": "世界第一最好的产品"
            },
            "marketing_content": [
                {"text": "全球首创独家技术"}
            ]
        }

        result = predictor.predict(platform_data)

        # 应该检测到虚假宣传风险
        false_advertising = next(
            (r for r in result["risk_assessments"] if r["risk_type"] == "虚假宣传"),
            None
        )
        assert false_advertising is not None
        assert false_advertising["probability"] > 0.3

    def test_risk_level_calculation(self, predictor):
        """测试风险等级计算"""
        assert predictor._calculate_risk_level(0.8) == "高"
        assert predictor._calculate_risk_level(0.5) == "中"
        assert predictor._calculate_risk_level(0.2) == "低"

    def test_predict_with_specific_risk_types(self, predictor):
        """测试指定风险类型预测"""
        platform_data = {
            "product_info": {"name": "测试"},
            "marketing_content": []
        }

        result = predictor.predict(
            platform_data,
            risk_types=["虚假宣传", "价格欺诈"]
        )

        assert len(result["risk_assessments"]) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
