"""
缓存模块测试
"""

import pytest
import time
from src.cache import MemoryCache, cached, get_global_cache


class TestMemoryCache:
    """内存缓存测试"""

    def test_set_and_get(self):
        """测试设置和获取"""
        cache = MemoryCache()
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_nonexistent(self):
        """测试获取不存在的键"""
        cache = MemoryCache()
        assert cache.get("nonexistent") is None

    def test_delete(self):
        """测试删除"""
        cache = MemoryCache()
        cache.set("key1", "value1")
        assert cache.delete("key1") is True
        assert cache.get("key1") is None

    def test_clear(self):
        """测试清空"""
        cache = MemoryCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_ttl_expiration(self):
        """测试TTL过期"""
        cache = MemoryCache(default_ttl=1)
        cache.set("key1", "value1", ttl=1)

        # 立即获取应该存在
        assert cache.get("key1") == "value1"

        # 等待过期
        time.sleep(1.5)
        assert cache.get("key1") is None

    def test_cache_stats(self):
        """测试缓存统计"""
        cache = MemoryCache()
        cache.set("key1", "value1")
        cache.get("key1")  # hit
        cache.get("key2")  # miss

        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["size"] == 1

    def test_max_size_limit(self):
        """测试最大缓存数量限制"""
        cache = MemoryCache(max_size=5)

        for i in range(10):
            cache.set(f"key{i}", f"value{i}")

        # 缓存数量应该不超过max_size
        assert len(cache._cache) <= 5


class TestCachedDecorator:
    """缓存装饰器测试"""

    def test_cached_function(self):
        """测试缓存装饰器"""
        call_count = 0

        @cached(ttl=60)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # 第一次调用
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # 第二次调用应该使用缓存
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # 没有增加

        # 不同参数应该重新计算
        result3 = expensive_function(10)
        assert result3 == 20
        assert call_count == 2

    def test_cache_clear(self):
        """测试缓存清除"""
        @cached(ttl=60)
        def func(x):
            return x

        func(1)
        func.cache_clear()

        stats = func.cache_stats()
        assert stats["size"] == 0


class TestGlobalCache:
    """全局缓存测试"""

    def test_get_global_cache(self):
        """测试获取全局缓存"""
        cache1 = get_global_cache()
        cache2 = get_global_cache()
        assert cache1 is cache2
