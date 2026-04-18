"""
缓存模块

提供内存缓存支持，减少重复计算。
"""

import time
from typing import Dict, Any, Optional, Callable
from functools import wraps
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class CacheItem:
    """缓存项"""

    def __init__(self, value: Any, ttl: int = 300):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl

    def is_expired(self) -> bool:
        """检查是否过期"""
        return time.time() - self.created_at > self.ttl


class MemoryCache:
    """内存缓存"""

    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        """
        初始化缓存

        Args:
            default_ttl: 默认过期时间（秒）
            max_size: 最大缓存数量
        """
        self._cache: Dict[str, CacheItem] = {}
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._hits = 0
        self._misses = 0

    def _generate_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = {
            "args": args,
            "kwargs": kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        item = self._cache.get(key)

        if item is None:
            self._misses += 1
            return None

        if item.is_expired():
            del self._cache[key]
            self._misses += 1
            return None

        self._hits += 1
        return item.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存值"""
        # 清理过期缓存
        if len(self._cache) >= self.max_size:
            self._cleanup()

        self._cache[key] = CacheItem(
            value=value,
            ttl=ttl or self.default_ttl
        )

    def delete(self, key: str) -> bool:
        """删除缓存"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()

    def _cleanup(self) -> None:
        """清理过期缓存"""
        expired_keys = [
            k for k, v in self._cache.items()
            if v.is_expired()
        ]
        for key in expired_keys:
            del self._cache[key]

        # 如果还是超过限制，删除最旧的
        if len(self._cache) >= self.max_size:
            # 按创建时间排序，删除最旧的
            sorted_items = sorted(
                self._cache.items(),
                key=lambda x: x[1].created_at
            )
            for key, _ in sorted_items[:len(sorted_items) - self.max_size // 2]:
                del self._cache[key]

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 3)
        }


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    缓存装饰器

    Args:
        ttl: 过期时间（秒）
        key_prefix: 键前缀
    """
    cache = MemoryCache(default_ttl=ttl)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            key = f"{key_prefix}:{cache._generate_key(*args, **kwargs)}"

            # 尝试获取缓存
            cached_value = cache.get(key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_value

            # 执行函数
            result = func(*args, **kwargs)

            # 存入缓存
            cache.set(key, result)
            logger.debug(f"Cache miss for {func.__name__}")

            return result

        # 添加缓存管理方法
        wrapper.cache = cache
        wrapper.cache_clear = cache.clear
        wrapper.cache_stats = cache.get_stats

        return wrapper

    return decorator


# 全局缓存实例
_global_cache = MemoryCache(default_ttl=300, max_size=2000)


def get_global_cache() -> MemoryCache:
    """获取全局缓存实例"""
    return _global_cache


def cache_prediction(platform_data: Dict, result: Dict, ttl: int = 600) -> None:
    """缓存预测结果"""
    key = hashlib.md5(
        json.dumps(platform_data, sort_keys=True, default=str).encode()
    ).hexdigest()
    _global_cache.set(f"pred:{key}", result, ttl)


def get_cached_prediction(platform_data: Dict) -> Optional[Dict]:
    """获取缓存的预测结果"""
    key = hashlib.md5(
        json.dumps(platform_data, sort_keys=True, default=str).encode()
    ).hexdigest()
    return _global_cache.get(f"pred:{key}")
