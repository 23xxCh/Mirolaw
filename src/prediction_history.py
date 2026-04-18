"""
预测历史记录模块

保存预测历史，支持历史查询和趋势分析。
"""

import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

# 数据目录
DATA_DIR = Path(__file__).parent.parent / "data" / "history"
DATA_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class PredictionRecord:
    """预测记录"""
    record_id: str = field(default_factory=lambda: hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:12])
    platform_data_hash: str = ""
    prediction_result: Dict = field(default_factory=dict)
    alerts_triggered: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


class PredictionHistory:
    """预测历史管理"""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or DATA_DIR
        self.records: Dict[str, PredictionRecord] = {}
        self._load_recent_records()

    def _load_recent_records(self):
        """加载最近7天的记录"""
        cutoff = datetime.now() - timedelta(days=7)

        for filepath in self.data_dir.glob("*.json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    record = PredictionRecord(**data)

                    # 只加载最近7天
                    record_time = datetime.fromisoformat(record.created_at)
                    if record_time > cutoff:
                        self.records[record.record_id] = record
            except Exception as e:
                logger.error(f"Failed to load record: {e}")

    def save_record(self, record: PredictionRecord) -> str:
        """保存记录"""
        self.records[record.record_id] = record

        # 写入文件
        filepath = self.data_dir / f"{record.record_id}.json"
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(record.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save record: {e}")

        return record.record_id

    def get_record(self, record_id: str) -> Optional[PredictionRecord]:
        """获取记录"""
        return self.records.get(record_id)

    def get_recent_records(self, limit: int = 50) -> List[PredictionRecord]:
        """获取最近记录"""
        sorted_records = sorted(
            self.records.values(),
            key=lambda r: r.created_at,
            reverse=True
        )
        return sorted_records[:limit]

    def get_records_by_date_range(
        self,
        start_date: str,
        end_date: str
    ) -> List[PredictionRecord]:
        """按日期范围查询"""
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        return [
            r for r in self.records.values()
            if start <= datetime.fromisoformat(r.created_at) <= end
        ]

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        if not self.records:
            return {
                "total": 0,
                "avg_risk_score": 0,
                "high_risk_count": 0,
                "alerts_triggered": 0
            }

        total_risk = 0
        high_risk_count = 0
        total_alerts = 0

        for record in self.records.values():
            score = record.prediction_result.get("overall_risk_score", 0)
            total_risk += score
            if score >= 0.7:
                high_risk_count += 1
            total_alerts += record.alerts_triggered

        return {
            "total": len(self.records),
            "avg_risk_score": round(total_risk / len(self.records), 3),
            "high_risk_count": high_risk_count,
            "alerts_triggered": total_alerts
        }

    def get_trend_data(self, days: int = 7) -> Dict:
        """获取趋势数据"""
        trend = []
        cutoff = datetime.now() - timedelta(days=days)

        # 按天分组
        daily_data = {}
        for record in self.records.values():
            record_time = datetime.fromisoformat(record.created_at)
            if record_time > cutoff:
                date_key = record_time.strftime("%Y-%m-%d")
                if date_key not in daily_data:
                    daily_data[date_key] = {
                        "count": 0,
                        "total_risk": 0,
                        "alerts": 0
                    }
                daily_data[date_key]["count"] += 1
                daily_data[date_key]["total_risk"] += record.prediction_result.get("overall_risk_score", 0)
                daily_data[date_key]["alerts"] += record.alerts_triggered

        # 生成趋势
        for date in sorted(daily_data.keys()):
            data = daily_data[date]
            trend.append({
                "date": date,
                "count": data["count"],
                "avg_risk": round(data["total_risk"] / data["count"], 3) if data["count"] > 0 else 0,
                "alerts": data["alerts"]
            })

        return {"trend": trend, "days": days}

    def delete_record(self, record_id: str) -> bool:
        """删除记录"""
        if record_id in self.records:
            del self.records[record_id]
            filepath = self.data_dir / f"{record_id}.json"
            if filepath.exists():
                filepath.unlink()
            return True
        return False

    def clear_old_records(self, days: int = 30):
        """清理旧记录"""
        cutoff = datetime.now() - timedelta(days=days)
        to_delete = []

        for record_id, record in self.records.items():
            record_time = datetime.fromisoformat(record.created_at)
            if record_time < cutoff:
                to_delete.append(record_id)

        for record_id in to_delete:
            self.delete_record(record_id)

        logger.info(f"Cleared {len(to_delete)} old records")
        return len(to_delete)


# 全局实例
_prediction_history = None


def get_prediction_history() -> PredictionHistory:
    """获取预测历史实例"""
    global _prediction_history
    if _prediction_history is None:
        _prediction_history = PredictionHistory()
    return _prediction_history
