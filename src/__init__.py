"""
电商合规哨兵 - 核心模块包

本包提供电商平台合规风险预测、罚款预测、知识图谱和应对建议生成等功能。

主要模块:
    - predictor: 风险预测模块
    - fine_predictor: 罚款预测模块
    - knowledge_graph: 法律知识图谱模块
    - suggestion_generator: 应对建议生成模块
    - api: FastAPI接口模块

版本: 0.1.0
作者: MiroLaw Team
"""

__version__ = "0.1.0"
__author__ = "MiroLaw Team"

from .predictor import RiskPredictor
from .fine_predictor import FinePredictor
from .knowledge_graph import LegalKnowledgeGraph
from .suggestion_generator import SuggestionGenerator

__all__ = [
    "RiskPredictor",
    "FinePredictor",
    "LegalKnowledgeGraph",
    "SuggestionGenerator",
]
