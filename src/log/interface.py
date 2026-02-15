from typing import Any, Protocol, overload


class Logger(Protocol):
    @overload
    def debug(__self, __message: str, *args: Any, **kwargs: Any) -> None: ...

    @overload
    def debug(__self, __message: Any) -> None: ...

    @overload
    def info(__self, __message: str, *args: Any, **kwargs: Any) -> None: ...

    @overload
    def info(__self, __message: Any) -> None: ...

    @overload
    def warning(__self, __message: str, *args: Any, **kwargs: Any) -> None: ...

    @overload
    def warning(__self, __message: Any) -> None: ...

    @overload
    def error(__self, __message: str, *args: Any, **kwargs: Any) -> None: ...

    @overload
    def error(__self, __message: Any) -> None: ...
