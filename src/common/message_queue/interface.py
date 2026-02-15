"""
双轨接口设计（Protocol + ABC）
- MessageQueue（Protocol）：用于 鸭子类型和静态类型检查（如类型提示、IDE 补全、mypy 检查）。
- BaseMessageQueue（ABC）：用于 强制子类实现所有方法（运行时保障）。
"""

from abc import ABC, abstractmethod
from typing import Generic, Optional, Protocol, TypeVar

T = TypeVar("T")


class MessageQueue(Protocol, Generic[T]):
    """通用消息队列协议。"""

    def put(self, item: T, timeout: Optional[float] = None) -> None:
        """入队；成功返回 True，队列满或关闭返回 False。"""
        ...

    def put_nowait(self, item: T) -> None:
        """非阻塞入队；成功返回 True，队列满或关闭返回 False。"""
        ...

    def get(self, timeout: Optional[float] = None) -> T:
        """出队；为空时抛出 QueueEmptyError。"""
        ...

    def get_nowait(self) -> T:
        """非阻塞出队；为空时抛出 QueueEmptyError。"""
        ...

    def task_done(self) -> None:
        """标记当前任务完成。"""
        ...

    def qsize(self) -> int:
        """返回当前队列长度。"""
        ...

    def maxsize(self) -> int:
        """返回队列容量上限。"""
        ...

    def close(self) -> None:
        """关闭队列并释放底层资源。"""
        ...


class BaseMessageQueue(ABC, Generic[T]):
    """通用消息队列抽象基类。"""

    @abstractmethod
    def put(self, item: T, timeout: Optional[float] = None) -> None:
        """入队；成功返回 True，队列满或关闭返回 False。"""
        raise NotImplementedError

    @abstractmethod
    def put_nowait(self, item: T) -> None:
        """非阻塞入队；成功返回 True，队列满或关闭返回 False。"""
        raise NotImplementedError

    @abstractmethod
    def get(self, timeout: Optional[float] = None) -> T:
        """出队；为空时抛出 QueueEmptyError。"""
        raise NotImplementedError

    @abstractmethod
    def get_nowait(self) -> T:
        """非阻塞出队；为空时抛出 QueueEmptyError。"""
        raise NotImplementedError

    @abstractmethod
    def task_done(self) -> None:
        """标记当前任务完成。"""
        raise NotImplementedError

    @abstractmethod
    def qsize(self) -> int:
        """返回当前队列长度。"""
        raise NotImplementedError

    @abstractmethod
    def maxsize(self) -> int:
        """返回队列容量上限。"""
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """关闭队列并释放底层资源。"""
        raise NotImplementedError
