"""
向量搜索引擎模块

使用sentence-transformers实现法律条文的语义搜索。
支持自然语言查询相关法律依据。
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

# 尝试导入向量搜索库
try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    VECTOR_SEARCH_AVAILABLE = True
except ImportError:
    VECTOR_SEARCH_AVAILABLE = False
    logger.warning("sentence-transformers not installed, using fallback keyword search")

# 尝试导入faiss
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("faiss not installed, using numpy for similarity")


class VectorSearchEngine:
    """向量搜索引擎"""

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """初始化向量搜索引擎"""
        self.model_name = model_name
        self.model = None
        self.embeddings = None
        self.documents = []
        self.index = None

        if VECTOR_SEARCH_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name)
                logger.info(f"Loaded embedding model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                self.model = None

    def is_available(self) -> bool:
        """检查向量搜索是否可用"""
        return self.model is not None

    def encode(self, texts: List[str]) -> "np.ndarray":
        """将文本转换为向量"""
        if self.model is None:
            return None
        return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

    def build_index(self, documents: List[Dict], text_key: str = "content"):
        """构建向量索引"""
        if not self.is_available():
            logger.warning("Vector search not available, skipping index build")
            return False

        self.documents = documents
        texts = [doc.get(text_key, "") for doc in documents]

        # 过滤空文本
        valid_indices = [i for i, t in enumerate(texts) if t.strip()]
        if not valid_indices:
            logger.warning("No valid documents to index")
            return False

        valid_texts = [texts[i] for i in valid_indices]
        self.documents = [documents[i] for i in valid_indices]

        # 生成向量
        self.embeddings = self.encode(valid_texts)

        if self.embeddings is None:
            return False

        # 构建索引
        if FAISS_AVAILABLE:
            dimension = self.embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(self.embeddings.astype('float32'))
            logger.info(f"Built FAISS index with {len(self.documents)} documents")
        else:
            logger.info(f"Built numpy index with {len(self.documents)} documents")

        return True

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """搜索相似文档"""
        if not self.is_available() or self.embeddings is None:
            return []

        # 编码查询
        query_embedding = self.encode([query])
        if query_embedding is None:
            return []

        # 搜索
        if FAISS_AVAILABLE and self.index is not None:
            D, I = self.index.search(query_embedding.astype('float32'), top_k)
            results = []
            for i, idx in enumerate(I[0]):
                if idx < len(self.documents):
                    results.append((self.documents[idx], float(D[0][i])))
            return results
        else:
            # 使用numpy计算余弦相似度
            from numpy.linalg import norm
            similarities = []
            for i, doc_embedding in enumerate(self.embeddings):
                cos_sim = np.dot(query_embedding[0], doc_embedding) / (norm(query_embedding[0]) * norm(doc_embedding))
                similarities.append((self.documents[i], float(cos_sim)))

            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:top_k]


class LegalVectorSearch:
    """法律向量搜索"""

    def __init__(self, law_database):
        """初始化法律向量搜索"""
        self.law_database = law_database
        self.engine = VectorSearchEngine()
        self._build_legal_index()

    def _build_legal_index(self):
        """构建法律条文向量索引"""
        documents = []

        for law_name, law_data in self.law_database.get_all_laws().items():
            for article in law_data.get("articles", []):
                documents.append({
                    "law_name": law_name,
                    "full_name": law_data.get("name", law_name),
                    "article_id": article.get("article_id", ""),
                    "content": article.get("content", ""),
                    "keywords": article.get("keywords", []),
                    "risk_types": article.get("risk_types", [])
                })

        if documents:
            self.engine.build_index(documents)
            logger.info(f"Built legal vector index with {len(documents)} articles")

    def _do_initialize(self):
        """Actually initialize the model and index"""
        if not self._check_available():
            return False

        try:
            from sentence_transformers import SentenceTransformer
            import faiss
            import numpy as np

            logger.info("Loading sentence-transformers model...")
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

            # Build index
            if self.documents:
                texts = [doc.get('content', '') for doc in self.documents]
                embeddings = self.model.encode(texts)
                dimension = embeddings.shape[1]
                self.index = faiss.IndexFlatL2(dimension)
                self.index.add(np.array(embeddings).astype('float32'))

            self._initialized = True
            logger.info("Vector search engine initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize vector search: {e}")
            self._available = False
            return False

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """搜索相关法律条文"""
        if not self.engine.is_available():
            # 回退到关键词搜索
            return self.law_database.search_articles(query, top_k)

        results = self.engine.search(query, top_k)
        return [
            {
                **doc,
                "similarity": score,
                "match_type": "semantic"
            }
            for doc, score in results
        ]

    def search_by_risk_context(self, risk_type: str, context: str, top_k: int = 3) -> List[Dict]:
        """根据风险类型和上下文搜索"""
        query = f"{risk_type} {context}"
        return self.search(query, top_k)


# 全局实例
_legal_vector_search = None


def get_legal_vector_search():
    """获取法律向量搜索实例"""
    global _legal_vector_search
    if _legal_vector_search is None:
        from .law_database import get_law_database
        law_db = get_law_database()
        _legal_vector_search = LegalVectorSearch(law_db)
    return _legal_vector_search
