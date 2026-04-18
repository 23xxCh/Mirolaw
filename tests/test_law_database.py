"""
单元测试 - 法律数据库模块
"""

import pytest
from src.law_database import LawDatabase, get_law_database


class TestLawDatabase:
    """法律数据库测试"""

    @pytest.fixture
    def db(self):
        return LawDatabase()

    def test_load_laws(self, db):
        """测试法律加载"""
        laws = db.get_all_laws()
        assert len(laws) > 0
        assert "广告法" in laws
        assert "电子商务法" in laws

    def test_search_articles(self, db):
        """测试条文搜索"""
        results = db.search_articles("虚假宣传")
        assert len(results) > 0

    def test_get_articles_by_risk_type(self, db):
        """测试按风险类型查询"""
        articles = db.get_articles_by_risk_type("虚假宣传")
        assert len(articles) > 0

        for article in articles:
            assert "虚假宣传" in article.get("risk_types", [])

    def test_get_statistics(self, db):
        """测试统计信息"""
        stats = db.get_statistics()
        assert "total_laws" in stats
        assert "total_articles" in stats
        assert stats["total_laws"] >= 8  # 至少8部法律


class TestLawDatabaseSingleton:
    """单例测试"""

    def test_singleton(self):
        """测试单例模式"""
        db1 = get_law_database()
        db2 = get_law_database()
        assert db1 is db2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
