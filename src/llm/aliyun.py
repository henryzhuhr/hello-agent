"""
https://help.aliyun.com/zh/model-studio/use-bailian-in-langchain


uv add langchain-community dashscope
"""

import os
from typing import List, Optional

from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    AnyMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_openai import ChatOpenAI
from pydantic import SecretStr


def get_default_apikey() -> str:
    return os.getenv("DASHSCOPE_API_KEY", "")


def init_qwen_chatmodel(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen-plus",
    apikey: Optional[str] = None,
) -> BaseChatModel:
    if apikey is None:
        apikey = get_default_apikey()
    chatLLM = ChatOpenAI(
        api_key=SecretStr(apikey),
        base_url=base_url,
        model=model,  # 此处以qwen-plus为例，您可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        # other params...
    )
    return chatLLM


def init_qwen_embeddings(
    model="text-embedding-v4",
    apikey: Optional[str] = None,
) -> Embeddings:
    if apikey is None:
        apikey = get_default_apikey()
    embeddings = DashScopeEmbeddings(
        model="text-embedding-v4",
        dashscope_api_key=apikey,
        # other params...
    )
    return embeddings


def test_qwen():
    chat_model = init_qwen_chatmodel()

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
        raise ConnectionError("failed to connect to Qwen server") from e
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

    conversation.append(HumanMessage(content="我刚才第一个问题问的是什么？"))

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
    test_qwen()
