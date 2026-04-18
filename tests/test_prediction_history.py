"""
预测历史记录测试
"""

import pytest
from datetime import datetime, timedelta
from src.prediction_history import PredictionRecord, PredictionHistory, get_prediction_history
import tempfile
import json
from pathlib import Path


class TestPredictionRecord:
    """预测记录测试"""

    def test_create_record(self):
        """测试创建记录"""
        record = PredictionRecord(
            prediction_result={"overall_risk_score": 0.5},
            alerts_triggered=2
        )

        assert record.record_id is not None
        assert len(record.record_id) == 12
        assert record.prediction_result["overall_risk_score"] == 0.5
        assert record.alerts_triggered == 2

    def test_to_dict(self):
        """测试转换为字典"""
        record = PredictionRecord(
            prediction_result={"overall_risk_score": 0.7},
            alerts_triggered=1,
            metadata={"test": "value"}
        )

        data = record.to_dict()
        assert isinstance(data, dict)
        assert data["prediction_result"]["overall_risk_score"] == 0.7
        assert data["alerts_triggered"] == 1
        assert data["metadata"]["test"] == "value"


class TestPredictionHistory:
    """预测历史管理测试"""

    @pytest.fixture
    def temp_history(self):
        """创建临时历史实例"""
        with tempfile.TemporaryDirectory() as tmpdir:
            history = PredictionHistory(data_dir=Path(tmpdir))
            yield history

    def test_save_record(self, temp_history):
        """测试保存记录"""
        record = PredictionRecord(
            prediction_result={"overall_risk_score": 0.6},
            alerts_triggered=0
        )

        record_id = temp_history.save_record(record)
        assert record_id == record.record_id

        # 验证可以获取
        retrieved = temp_history.get_record(record_id)
        assert retrieved is not None
        assert retrieved.prediction_result["overall_risk_score"] == 0.6

    def test_get_recent_records(self, temp_history):
        """测试获取最近记录"""
        # 添加多条记录
        for i in range(5):
            record = PredictionRecord(
                prediction_result={"overall_risk_score": i * 0.1},
                alerts_triggered=i
            )
            temp_history.save_record(record)

        records = temp_history.get_recent_records(limit=3)
        assert len(records) == 3

    def test_get_statistics(self, temp_history):
        """测试获取统计"""
        # 添加记录
        for score in [0.3, 0.5, 0.8, 0.9]:
            record = PredictionRecord(
                prediction_result={"overall_risk_score": score},
                alerts_triggered=1 if score >= 0.7 else 0
            )
            temp_history.save_record(record)

        stats = temp_history.get_statistics()
        assert stats["total"] == 4
        assert stats["avg_risk_score"] == 0.625
        assert stats["high_risk_count"] == 2
        assert stats["alerts_triggered"] == 2

    def test_get_trend_data(self, temp_history):
        """测试获取趋势数据"""
        # 添加记录
        for i in range(3):
            record = PredictionRecord(
                prediction_result={"overall_risk_score": 0.5},
                alerts_triggered=1
            )
            temp_history.save_record(record)

        trend = temp_history.get_trend_data(days=7)
        assert "trend" in trend
        assert trend["days"] == 7

    def test_delete_record(self, temp_history):
        """测试删除记录"""
        record = PredictionRecord(
            prediction_result={"overall_risk_score": 0.5},
            alerts_triggered=0
        )
        record_id = temp_history.save_record(record)

        # 删除
        success = temp_history.delete_record(record_id)
        assert success is True

        # 验证已删除
        retrieved = temp_history.get_record(record_id)
        assert retrieved is None

    def test_singleton(self):
        """测试单例模式"""
        history1 = get_prediction_history()
        history2 = get_prediction_history()
        assert history1 is history2
