"""
单元测试 - 知识图谱模块
"""

import pytest
from src.knowledge_graph import LegalKnowledgeGraph


class TestKnowledgeGraph:
    """知识图谱测试"""

    @pytest.fixture
    def kg(self):
        return LegalKnowledgeGraph()

    def test_query_similar_cases(self, kg):
        """测试案例查询"""
        cases = kg.query_similar_cases("虚假宣传")
        assert isinstance(cases, list)
        assert len(cases) > 0

    def test_get_legal_basis(self, kg):
        """测试法律依据查询"""
        basis = kg.get_legal_basis("虚假宣传")
        assert isinstance(basis, list)

    def test_add_case(self, kg):
        """测试添加案例"""
        case_data = {
            "case_id": "TEST001",
            "title": "测试案例",
            "risk_type": "虚假宣传",
            "fine_amount": 100000
        }

        result = kg.add_case(case_data)
        assert result is True

        # 验证添加成功
        cases = kg.query_similar_cases("虚假宣传")
        assert any(c["case_id"] == "TEST001" for c in cases)

    def test_get_statistics(self, kg):
        """测试统计信息"""
        stats = kg.get_risk_type_statistics()
        assert isinstance(stats, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
