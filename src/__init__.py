"""
电商合规哨兵 - 核心模块包

本包提供电商平台合规风险预测、罚款预测、知识图谱、实时预警和应对建议生成等功能。

主要模块:
    - predictor: 风险预测模块
    - fine_predictor: 罚款预测模块
    - knowledge_graph: 法律知识图谱模块
    - law_database: 法律数据库模块
    - alert_system: 实时预警系统
    - multi_agent: 多Agent协作模块
    - vector_search: 向量语义搜索
    - prediction_history: 预测历史记录
    - cache: 缓存模块
    - rate_limiter: API限流模块
    - task_queue: 异步任务队列
    - health_check: 健康检查模块
    - suggestion_generator: 应对建议生成模块
    - api: FastAPI接口模块

版本: 0.5.0
作者: MiroLaw Team
"""

__version__ = "0.5.0"
__author__ = "MiroLaw Team"

from .predictor import RiskPredictor
from .fine_predictor import FinePredictor
from .knowledge_graph import LegalKnowledgeGraph
from .law_database import LawDatabase
from .alert_system import AlertManager, AlertLevel
from .suggestion_generator import SuggestionGenerator
from .sample_data import get_sample_data, get_all_sample_data

__all__ = [
    "RiskPredictor",
    "FinePredictor",
    "LegalKnowledgeGraph",
    "LawDatabase",
    "AlertManager",
    "AlertLevel",
    "SuggestionGenerator",
    "get_sample_data",
    "get_all_sample_data",
]
