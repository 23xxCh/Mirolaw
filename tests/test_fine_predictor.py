"""
单元测试 - 罚款预测模块
"""

import pytest
from src.fine_predictor import FinePredictor
from src.knowledge_graph import LegalKnowledgeGraph


class TestFinePredictor:
    """罚款预测器测试"""

    @pytest.fixture
    def predictor(self):
        kg = LegalKnowledgeGraph()
        return FinePredictor(knowledge_graph=kg)

    def test_predict_fine(self, predictor):
        """测试罚款预测"""
        platform_data = {
            "company_size": "中型",
            "annual_revenue": 10000000
        }

        simulation_result = {
            "probability": 0.75,
            "risk_level": "高"
        }

        result = predictor.predict_fine(
            "虚假宣传",
            platform_data,
            simulation_result
        )

        assert "fine_range" in result
        assert "min" in result["fine_range"]
        assert "max" in result["fine_range"]
        assert "expected" in result["fine_range"]
        assert result["fine_range"]["expected"] > 0

    def test_fine_adjustment_by_company_size(self, predictor):
        """测试企业规模对罚款的影响"""
        simulation_result = {"probability": 0.5}

        # 大型企业
        large_result = predictor.predict_fine(
            "虚假宣传",
            {"company_size": "大型"},
            simulation_result
        )

        # 小型企业
        small_result = predictor.predict_fine(
            "虚假宣传",
            {"company_size": "小型"},
            simulation_result
        )

        # 大型企业罚款应该更高
        assert large_result["fine_range"]["expected"] >= small_result["fine_range"]["expected"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
