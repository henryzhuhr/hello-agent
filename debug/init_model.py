from langchain.chat_models import init_chat_model


def main():
    chat_model = init_chat_model(
        model="qwen3:0.6b",
        model_provider="ollama",  # 提供商
        # api_key="your-api-key",  # API 密钥（可选，可从环境变量读取）
        temperature=0.7,  # 温度参数（可选）
        max_tokens=1000,  # 最大 token 数（可选）
        # **kwargs,  # 其他模型特定参数
    )

    input_str = "什么是机器学习？用一句话解释"

    response = chat_model.invoke(input_str, config=None)


if __name__ == "__main__":
    main()
