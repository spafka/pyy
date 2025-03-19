import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient

from myclient import model_client


# 定义一个工具函数，用于查询天气
async def get_weather(city: str, units: str = "imperial") -> str:
    if units == "imperial":
        return f"The weather in {city} is 73 °F and Sunny."
    elif units == "metric":
        return f"The weather in {city} is 23 °C and Sunny."
    else:
        return f"Sorry, I don't know the weather in {city}."

async def main():
    # 创建一个OpenAI模型客户端

    # 创建一个AssistantAgent智能体，并添加工具函数
    assistant_agent = AssistantAgent(
        name="assistant_agent",
        model_client=model_client,
        tools=[get_weather],  # 添加天气查询工具
        system_message="你是一个助手，你可以使用get_weather 获取天气情况",
        reflect_on_tool_use=True
    )
    # 用户提问
    user_input = "纽约天气怎么样?"
    # 调用AssistantAgent的on_messages方法处理用户输入
    response = await assistant_agent.on_messages(
        [TextMessage(content=user_input, source="user")],
        CancellationToken()
    )
    # 打印AssistantAgent的响应
    print("Assistant:", response.chat_message.content)

asyncio.run(main())
