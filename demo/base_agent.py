from typing import List

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, ToolMessage

from llm.ollama_chat import init_ollama_chatmodel
from tools import weather


def main():
    tools = [weather.get_weather]

    chat_model = init_ollama_chatmodel()  # 初始化 Ollama ChatModel

    agent = create_agent(chat_model, tools=tools)

    """
    Mode	    Description
    ----        -----------
    values	    Streams the full value of the state after each step of the graph.
    updates	    Streams the updates to the state after each step of the graph. If multiple updates are made in the same step (e.g., multiple nodes are run), those updates are streamed separately.
    custom	    Streams custom data from inside your graph nodes.
    messages    Streams 2-tuples (LLM token, metadata) from any graph nodes where an LLM is invoked.
    debug	    Streams as much information as possible throughout the execution of the graph.
    """
    if False:
        for chunk in agent.stream(
            {"messages": [HumanMessage("请告诉我北京和上海的天气情况。")]},
            stream_mode="values",
        ):
            messages: List[AnyMessage] = chunk.get("messages", [])
            latest_message = messages[-1] if messages else AIMessage(content=None)
            if isinstance(latest_message, HumanMessage):
                print(f"🙋 User : {latest_message.content}")
            elif isinstance(latest_message, AIMessage):
                print(f"🤖 Agent: {latest_message.content}")
            elif isinstance(latest_message, ToolMessage):
                print(f"🛠️ Tool : {latest_message.content}")
            else:
                print(f"Message : {type(latest_message)} -- {latest_message.content}")
    if True:
        for chunk in agent.stream(
            {"messages": [HumanMessage("请告诉我北京和上海的天气情况。")]},
            stream_mode="updates",
        ):
            for step, data in chunk.items():
                messages: List[AnyMessage] = data.get("messages", [])
                latest_message = messages[-1] if messages else AIMessage(content=None)
                if isinstance(latest_message, HumanMessage):
                    print(f"🙋 User : {latest_message.content}")
                elif isinstance(latest_message, AIMessage):
                    if latest_message.tool_calls:
                        print("🤖 Agent (ToolCall):")
                        for tool_call in latest_message.tool_calls:
                            print(f"  🔨 ToolCall: {tool_call}")
                    else:
                        print(f"🤖 Agent: {latest_message.content}")
                elif isinstance(latest_message, ToolMessage):
                    print(f"🔨 Tool : {latest_message.content}")
                else:
                    print(f"Message : {type(latest_message)} -- {latest_message}")
                print()


if __name__ == "__main__":
    main()
