import time
from math import ceil
from typing import Any, Callable, Generic, TypeVar, cast

from .exceptions import QueueClosedError, QueueEmptyError, QueueFullError
from .interface import BaseMessageQueue

T = TypeVar("T")


class RedisQueueAdapter(BaseMessageQueue[T], Generic[T]):
    """
    基于 Redis List 的消息队列实现。

    注意：此实现依赖 redis-py，且默认使用序列化/反序列化函数处理消息体。
    """

    _client: Any
    """redis-py 客户端实例（由 Redis.from_url 创建）"""

    _queue_key: str
    """Redis List 对应的 key。"""

    _serializer: Callable[[T], str]
    """入队序列化函数。"""

    _deserializer: Callable[[str], T]
    """出队反序列化函数。"""

    _maxsize: int
    """队列容量上限，0 表示不限制。"""

    _closed: bool
    """队列是否已关闭。"""

    def __init__(
        self,
        *,
        redis_url: str,
        queue_key: str,
        serializer: Callable[[T], str],
        deserializer: Callable[[str], T],
        maxsize: int = 0,
    ) -> None:
        try:
            from redis import Redis
        except ImportError as exc:
            raise ImportError(
                "redis package is required for RedisQueueAdapter. Install with: uv add redis"
            ) from exc

        self._client: Any = Redis.from_url(redis_url, decode_responses=True)
        self._queue_key: str = queue_key
        self._serializer: Callable[[T], str] = serializer
        self._deserializer: Callable[[str], T] = deserializer
        self._maxsize: int = maxsize
        self._closed: bool = False

    def put(self, item: T, timeout: float | None = None) -> None:
        if self._closed:
            raise QueueClosedError("queue is closed")

        if timeout is None:
            self.put_nowait(item)
            return

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                self.put_nowait(item)
                return
            except QueueFullError:
                # Redis List 不提供容量阻塞写，这里用轮询重试模拟超时入队。
                pass
            time.sleep(0.01)
        raise QueueFullError("queue is full")

    def put_nowait(self, item: T) -> None:
        if self._closed:
            raise QueueClosedError("queue is closed")
        if self._maxsize > 0 and self.qsize() >= self._maxsize:
            raise QueueFullError("queue is full")
        self._client.rpush(self._queue_key, self._serializer(item))

    def get(self, timeout: float | None = None) -> T:
        if timeout is None:
            result = cast(
                list[str] | None, self._client.blpop([self._queue_key], timeout=0)
            )
        else:
            # Redis blpop 的 timeout 以秒为整数，向上取整避免提前超时。
            redis_timeout = max(1, ceil(timeout))
            result = cast(
                list[str] | None,
                self._client.blpop([self._queue_key], timeout=redis_timeout),
            )
        if result is None:
            raise QueueEmptyError("queue is empty")
        payload = result[1]
        return self._deserializer(payload)

    def get_nowait(self) -> T:
        payload = cast(str | None, self._client.lpop(self._queue_key))
        if payload is None:
            raise QueueEmptyError("queue is empty")
        return self._deserializer(payload)

    def task_done(self) -> None:
        # Redis List 无本地任务计数语义，保留空实现用于接口兼容。
        return None

    def qsize(self) -> int:
        return cast(int, self._client.llen(self._queue_key))

    def maxsize(self) -> int:
        return self._maxsize

    def close(self) -> None:
        self._closed = True
        self._client.close()
