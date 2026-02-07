import os
from typing import List

from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    AnyMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_ollama import ChatOllama

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_LLM_MODEL = "qwen3:0.6b"


def init_ollama_chatmodel(
    base_url: str = OLLAMA_BASE_URL,
    model: str = DEFAULT_LLM_MODEL,
    temperature=0.5,
    num_predict=256,
):
    """
    0.0-0.3：需要一致性、准确性的任务（数据提取、分类、代码生成）
    0.5-0.7：平衡创造性和一致性（聊天、问答）
    0.8-1.5：创造性任务（写作、头脑风暴）
    1.5-2.0：高度创造性（诗歌、故事创作）
    """
    ollama_chat = ChatOllama(
        model=model,
        base_url=base_url,
        validate_model_on_init=True,
        # temperature=temperature,
        # num_predict=num_predict,
    )
    return ollama_chat


def test_ollama():
    chat_model = init_ollama_chatmodel(model=DEFAULT_LLM_MODEL)

    conversation: List[AnyMessage] = [
        SystemMessage(content="你是一个的 Python 助手，回答要简洁明了。"),
        HumanMessage(content="我想学习 Python，从哪里开始？"),
    ]

    response = AIMessage(content="")
    try:
        response: AIMessage = chat_model.invoke(conversation)
    except ValueError as e:
        raise ValueError("invalid configuration") from e
    except ConnectionError as e:
        raise ConnectionError("failed to connect to Ollama server") from e
    except Exception as e:
        raise Exception("an error occurred during the request") from e
    print(f"🤖 ai: {response.model_dump_json()}")

    conversation.append(HumanMessage(content="数据类型有哪些？"))
    response: AIMessage = chat_model.invoke(conversation)
    print(f"🤖 ai: {response.model_dump_json()}")

    conversation.append(HumanMessage(content="我刚才第一个问题问的是什么？"))
    response: AIMessage = chat_model.invoke(conversation)
    print(f"🤖 ai: {response.model_dump_json()}")

    # 1. 主要内容
    # response.content  # str - AI 的回复文本
    # response.response_metadata  # dict - 响应元数据
    # response.id  # str - 消息唯一 ID
    # response.usage_metadata  # dict - Token 使用情况
    # response.additional_kwargs  # dict - 其他额外信息

    """
    # stream: https://docs.langchain.com/oss/python/langchain/models#stream
    """

    print("\nStreaming response:")

    conversation.append(HumanMessage(content="数据类型有哪些？"))

    full: AIMessageChunk = AIMessageChunk(content="")
    for chunk in chat_model.stream(conversation):
        # print(chunk.text, end=" ", flush=True)
        if chunk.response_metadata:
            print(chunk.model_dump_json())
            response_metadata = chunk.response_metadata
            # if response_metadata.get("")
        else:
            full = chunk if full is None else full + chunk
            print(f"full.text: {full.text}")
    print()


if __name__ == "__main__":
    test_ollama()
