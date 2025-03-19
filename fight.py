import asyncio
from typing import Any, Dict, List
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination
from autogen_agentchat.messages import HandoffMessage
from autogen_agentchat.teams import Swarm
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

from myclient import model_client


# 定义退款工具函数
def refund_flight(flight_id: str) -> str:
    return f"Flight {flight_id} refunded"


# 创建旅行代理智能体
travel_agent = AssistantAgent(
    "travel_agent",
    model_client=model_client,
    handoffs=["flights_refunder", "user"],
    system_message="""You are a travel agent. The flights_refunder is in charge of refunding flights. If you need information from the user, you must first send your message, then you can handoff to the user. Use TERMINATE when the travel planning is complete.""",
)

# 创建航班退款专员智能体
flights_refunder = AssistantAgent(
    "flights_refunder",
    model_client=model_client,
    handoffs=["travel_agent", "user"],
    tools=[refund_flight],
    system_message="""You are an agent specialized in refunding flights. You only need flight reference numbers to refund a flight. You have the ability to refund a flight using the refund_flight tool. If you need information from the user, you must first send your message, then you can handoff to the user. When the transaction is complete, handoff to the travel agent to finalize.""",
)

# 设置终止条件
termination = HandoffTermination(target="user") | TextMentionTermination("TERMINATE")
team = Swarm([travel_agent, flights_refunder], termination_condition=termination)

# 定义任务
task = "I need to refund my flight."

async def run_team_stream():
    task_result = await Console(team.run_stream(task=task))
    last_message = task_result.messages[-1]

    while isinstance(last_message, HandoffMessage) and last_message.target == "user":
        user_message = input("User: ")

        task_result = await Console(
            team.run_stream(task=HandoffMessage(source="user", target=last_message.source, content=user_message))
        )
        last_message = task_result.messages[-1]

# 运行任务
# Use asyncio.run(...) if you are running this in a script.
if __name__ == '__main__':
    asyncio.run( run_team_stream())
