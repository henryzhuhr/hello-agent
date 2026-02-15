import pytest

from src.common.message_queue.exceptions import (
    QueueClosedError,
    QueueEmptyError,
    QueueFullError,
)
from src.common.message_queue.inmemory_mq import InMemoryQueueAdapter


class TestInMemoryQueueAdapter:
    def test_basic_put_get(self) -> None:
        queue = InMemoryQueueAdapter[int](maxsize=2)

        queue.put_nowait(1)
        queue.put(2)

        assert queue.qsize() == 2
        assert queue.maxsize() == 2
        assert queue.get_nowait() == 1
        assert queue.get() == 2

    def test_full_and_empty_errors(self) -> None:
        queue = InMemoryQueueAdapter[str](maxsize=1)

        queue.put_nowait("a")
        with pytest.raises(QueueFullError):
            queue.put_nowait("b")

        assert queue.get_nowait() == "a"
        with pytest.raises(QueueEmptyError):
            queue.get(timeout=0.01)

    def test_closed_and_task_done_errors(self) -> None:
        queue = InMemoryQueueAdapter[str](maxsize=1)
        queue.close()

        with pytest.raises(QueueClosedError):
            queue.put("x")
        with pytest.raises(QueueClosedError):
            queue.put_nowait("x")
        with pytest.raises(QueueClosedError):
            queue.task_done()
