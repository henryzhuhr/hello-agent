import sys
import types

import pytest

import src.common.message_queue.redis_mq as redis_queue_module
from src.common.message_queue.exceptions import (
    QueueClosedError,
    QueueEmptyError,
    QueueFullError,
)
from src.common.message_queue.redis_mq import RedisQueueAdapter


@pytest.fixture
def fake_redis(monkeypatch: pytest.MonkeyPatch):
    class FakeRedisClient:
        def __init__(self) -> None:
            self._items: list[str] = []
            self.closed = False
            self.blpop_calls: list[tuple[str, int]] = []

        def rpush(self, _key: str, value: str) -> None:
            self._items.append(value)

        def lpop(self, _key: str):
            if not self._items:
                return None
            return self._items.pop(0)

        def blpop(self, key: str, timeout: int):
            self.blpop_calls.append((key, timeout))
            if not self._items:
                return None
            return (key, self._items.pop(0))

        def llen(self, _key: str) -> int:
            return len(self._items)

        def close(self) -> None:
            self.closed = True

    class FakeRedis:
        last_client: FakeRedisClient | None = None

        @classmethod
        def from_url(cls, _redis_url: str, decode_responses: bool = True):
            assert decode_responses is True
            cls.last_client = FakeRedisClient()
            return cls.last_client

    monkeypatch.setitem(sys.modules, "redis", types.SimpleNamespace(Redis=FakeRedis))
    return FakeRedis


class TestRedisQueueAdapter:
    def test_basic_put_get_and_size(self, fake_redis) -> None:
        queue = RedisQueueAdapter[int](
            redis_url="redis://unused",
            queue_key="mq:test",
            serializer=str,
            deserializer=int,
            maxsize=2,
        )

        queue.put_nowait(1)
        queue.put(2)

        assert queue.qsize() == 2
        assert queue.maxsize() == 2
        assert queue.get_nowait() == 1
        assert queue.get() == 2

    def test_full_empty_and_closed_errors(self, fake_redis) -> None:
        queue = RedisQueueAdapter[str](
            redis_url="redis://unused",
            queue_key="mq:test",
            serializer=str,
            deserializer=str,
            maxsize=1,
        )

        queue.put_nowait("a")
        with pytest.raises(QueueFullError):
            queue.put_nowait("b")

        assert queue.get_nowait() == "a"
        with pytest.raises(QueueEmptyError):
            queue.get_nowait()

        queue.close()
        with pytest.raises(QueueClosedError):
            queue.put("x")
        assert fake_redis.last_client is not None and fake_redis.last_client.closed is True

    def test_get_timeout_uses_ceil(self, fake_redis) -> None:
        queue = RedisQueueAdapter[str](
            redis_url="redis://unused",
            queue_key="mq:test",
            serializer=str,
            deserializer=str,
            maxsize=0,
        )
        queue.put_nowait("x")

        assert queue.get(timeout=0.2) == "x"
        assert fake_redis.last_client is not None
        assert fake_redis.last_client.blpop_calls[-1] == (["mq:test"], 1)

    def test_put_with_timeout_retries(self, monkeypatch: pytest.MonkeyPatch, fake_redis) -> None:
        queue = RedisQueueAdapter[str](
            redis_url="redis://unused",
            queue_key="mq:test",
            serializer=str,
            deserializer=str,
            maxsize=0,
        )

        monotonic_values = iter([0.0, 0.01, 0.02, 0.03])
        monkeypatch.setattr(redis_queue_module.time, "monotonic", lambda: next(monotonic_values))
        sleep_calls: list[float] = []
        monkeypatch.setattr(redis_queue_module.time, "sleep", lambda value: sleep_calls.append(value))

        attempts = {"count": 0}

        def flaky_put_nowait(_item: str) -> None:
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise QueueFullError("queue is full")

        monkeypatch.setattr(queue, "put_nowait", flaky_put_nowait)
        queue.put("x", timeout=0.05)

        assert attempts["count"] == 3
        assert sleep_calls == [0.01, 0.01]
