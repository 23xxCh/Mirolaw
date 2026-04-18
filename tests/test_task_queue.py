"""
任务队列模块测试
"""

import pytest
from src.task_queue import TaskQueue, TaskStatus, Task, get_task_queue


class TestTask:
    """任务测试"""

    def test_create_task(self):
        """测试创建任务"""
        task = Task(
            task_id="test123",
            name="test_task"
        )
        assert task.task_id == "test123"
        assert task.name == "test_task"
        assert task.status == TaskStatus.PENDING
        assert task.progress == 0.0

    def test_task_status_enum(self):
        """测试任务状态枚举"""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"


class TestTaskQueue:
    """任务队列测试"""

    def test_create_queue(self):
        """测试创建队列"""
        queue = TaskQueue(max_concurrent=5)
        assert queue.max_concurrent == 5
        assert queue._running_count == 0

    def test_get_stats(self):
        """测试获取统计"""
        queue = TaskQueue()
        stats = queue.get_stats()

        assert stats["total_tasks"] == 0
        assert stats["running_count"] == 0
        assert "status_counts" in stats

    def test_get_task_not_found(self):
        """测试获取不存在的任务"""
        queue = TaskQueue()
        task = queue.get_task("nonexistent")
        assert task is None

    def test_get_all_tasks_empty(self):
        """测试获取空任务列表"""
        queue = TaskQueue()
        tasks = queue.get_all_tasks()
        assert tasks == []

    def test_cancel_nonexistent_task(self):
        """测试取消不存在的任务"""
        queue = TaskQueue()
        success = queue.cancel_task("nonexistent")
        assert success is False

    def test_add_task_manually(self):
        """测试手动添加任务"""
        queue = TaskQueue()
        task = Task(task_id="test123", name="manual_task")
        queue.tasks["test123"] = task

        retrieved = queue.get_task("test123")
        assert retrieved is not None
        assert retrieved.name == "manual_task"

    def test_get_all_tasks_with_filter(self):
        """测试带过滤获取任务列表"""
        queue = TaskQueue()

        # 添加不同状态的任务
        task1 = Task(task_id="t1", name="task1", status=TaskStatus.PENDING)
        task2 = Task(task_id="t2", name="task2", status=TaskStatus.COMPLETED)

        queue.tasks["t1"] = task1
        queue.tasks["t2"] = task2

        pending = queue.get_all_tasks(status=TaskStatus.PENDING)
        assert len(pending) == 1
        assert pending[0].task_id == "t1"

    def test_clear_completed(self):
        """测试清理已完成任务"""
        queue = TaskQueue()

        task1 = Task(task_id="t1", name="task1", status=TaskStatus.COMPLETED)
        task2 = Task(task_id="t2", name="task2", status=TaskStatus.PENDING)

        queue.tasks["t1"] = task1
        queue.tasks["t2"] = task2

        cleared = queue.clear_completed()
        assert cleared == 1
        assert "t1" not in queue.tasks
        assert "t2" in queue.tasks

    def test_singleton(self):
        """测试单例模式"""
        queue1 = get_task_queue()
        queue2 = get_task_queue()
        assert queue1 is queue2
