import queue
import threading
from typing import Generic, TypeVar

from .exceptions import QueueClosedError, QueueEmptyError, QueueFullError
from .interface import BaseMessageQueue

T = TypeVar("T")


class InMemoryQueueAdapter(BaseMessageQueue[T], Generic[T]):
    """基于内置 queue.Queue 的消息队列实现。"""

    _queue: queue.Queue[T]
    """底层内存队列实例"""

    _closed: bool
    """队列是否已关闭标记"""

    _state_lock: threading.Lock
    """保护关闭状态读写的互斥锁"""

    def __init__(self, maxsize: int = 100) -> None:
        self._queue: queue.Queue[T] = queue.Queue(maxsize=maxsize)
        self._closed: bool = False
        self._state_lock: threading.Lock = threading.Lock()

    def put(self, item: T, timeout: float | None = None) -> None:
        # close 仅影响后续入队；加锁保证关闭状态检查与入队前判断一致。
        with self._state_lock:
            if self._closed:
                raise QueueClosedError("queue is closed")
        try:
            if timeout is None:
                self._queue.put(item, block=True)
            else:
                self._queue.put(item, block=True, timeout=timeout)
        except queue.Full as exc:
            raise QueueFullError("queue is full") from exc

    def put_nowait(self, item: T) -> None:
        # 与 put 保持相同的关闭语义。
        with self._state_lock:
            if self._closed:
                raise QueueClosedError("queue is closed")
        try:
            self._queue.put_nowait(item)
        except queue.Full as exc:
            raise QueueFullError("queue is full") from exc

    def get(self, timeout: float | None = None) -> T:
        try:
            if timeout is None:
                return self._queue.get(block=True)
            return self._queue.get(block=True, timeout=timeout)
        except queue.Empty as exc:
            raise QueueEmptyError("queue is empty") from exc

    def get_nowait(self) -> T:
        try:
            return self._queue.get_nowait()
        except queue.Empty as exc:
            raise QueueEmptyError("queue is empty") from exc

    def task_done(self) -> None:
        try:
            self._queue.task_done()
        except ValueError as exc:
            # queue.Queue 在未完成 get 配对时会抛 ValueError，这里统一映射为队列语义错误。
            raise QueueClosedError("task_done called too many times") from exc

    def qsize(self) -> int:
        return self._queue.qsize()

    def maxsize(self) -> int:
        return self._queue.maxsize

    def close(self) -> None:
        with self._state_lock:
            self._closed = True
