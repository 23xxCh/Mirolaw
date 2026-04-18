"""
异步任务队列模块

支持长时间运行的任务后台处理。
"""

import asyncio
import uuid
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """任务"""
    task_id: str
    name: str
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    progress: float = 0.0
    metadata: Dict = field(default_factory=dict)


class TaskQueue:
    """任务队列"""

    def __init__(self, max_concurrent: int = 5):
        self.tasks: Dict[str, Task] = {}
        self.max_concurrent = max_concurrent
        self._running_count = 0
        self._queue: asyncio.Queue = asyncio.Queue()

    async def submit(
        self,
        name: str,
        func: Callable,
        *args,
        **kwargs
    ) -> str:
        """提交任务"""
        task_id = str(uuid.uuid4())[:12]

        task = Task(
            task_id=task_id,
            name=name,
            metadata={"func": func.__name__, "args": str(args)[:100]}
        )
        self.tasks[task_id] = task

        # 加入队列
        await self._queue.put((task_id, func, args, kwargs))

        # 启动处理
        asyncio.create_task(self._process_queue())

        logger.info(f"Task {task_id} submitted: {name}")
        return task_id

    async def _process_queue(self):
        """处理队列"""
        if self._running_count >= self.max_concurrent:
            return

        try:
            task_id, func, args, kwargs = self._queue.get_nowait()
        except asyncio.QueueEmpty:
            return

        task = self.tasks.get(task_id)
        if not task:
            return

        self._running_count += 1
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now().isoformat()

        try:
            # 执行任务
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
            logger.info(f"Task {task_id} completed")

        except asyncio.CancelledError:
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now().isoformat()
            logger.info(f"Task {task_id} cancelled")

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now().isoformat()
            logger.error(f"Task {task_id} failed: {e}")

        finally:
            self._running_count -= 1

    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self.tasks.get(task_id)

    def get_all_tasks(self, status: Optional[TaskStatus] = None) -> list:
        """获取所有任务"""
        tasks = list(self.tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)

    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        task = self.tasks.get(task_id)
        if task and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now().isoformat()
            return True
        return False

    def clear_completed(self) -> int:
        """清理已完成任务"""
        to_remove = [
            tid for tid, t in self.tasks.items()
            if t.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
        ]
        for tid in to_remove:
            del self.tasks[tid]
        return len(to_remove)

    def get_stats(self) -> Dict:
        """获取统计"""
        status_counts = {}
        for status in TaskStatus:
            status_counts[status.value] = len([
                t for t in self.tasks.values() if t.status == status
            ])

        return {
            "total_tasks": len(self.tasks),
            "running_count": self._running_count,
            "max_concurrent": self.max_concurrent,
            "queue_size": self._queue.qsize(),
            "status_counts": status_counts
        }


# 全局任务队列
_task_queue = None


def get_task_queue() -> TaskQueue:
    """获取任务队列实例"""
    global _task_queue
    if _task_queue is None:
        _task_queue = TaskQueue()
    return _task_queue
