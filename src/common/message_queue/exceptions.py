class MessageQueueError(Exception):
    """消息队列基础异常。"""

    pass


class QueueFullError(MessageQueueError):
    """消息队列已满。"""

    pass


class QueueEmptyError(MessageQueueError):
    """消息队列为空。"""

    pass


class QueueClosedError(MessageQueueError):
    """消息队列已关闭。"""

    pass
