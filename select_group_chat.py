import asyncio
from typing import Sequence
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import AgentEvent, ChatMessage
from autogen_agentchat.teams import SelectorGroupChat, Swarm
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

from myclient import model_client


def search_web_tool(query: str) -> str:
    if "2006-2007" in query:
        return """Here are the total points scored by Miami Heat players in the 2006-2007 season:
        Udonis Haslem: 844 points
        Dwayne Wade: 1397 points
        James Posey: 550 points
      ...
        """
    elif "2007-2008" in query:
        return "The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214."
    elif "2008-2009" in query:
        return "The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398."
    return "No data found."


def percentage_change_tool(start: float, end: float) -> float:
    return ((end - start) / start) * 100


def create_team() -> SelectorGroupChat:
    planning_agent = AssistantAgent(
        "PlanningAgent",
        description="An agent for planning tasks, this agent should be the first to engage when given a new task.",
        model_client=model_client,
        handoffs=['web_search_agent'],
        system_message="""
你是一名规划代理人。
你的工作是将复杂的任务分解为更小、可管理的子任务。
您的团队成员包括：
Web搜索代理：搜索信息
数据分析师：执行计算
你只计划和委派任务，而不是自己执行。
分配任务时，请使用以下格式：
<代理>：<任务>
所有任务完成后，总结结果并以“TERMINATE”结束。
        """,
    )
    web_search_agent = AssistantAgent(
        "web_search_agent",
        description="A web search agent.",
        tools=[search_web_tool],
        model_client=model_client,
        handoffs=['data_analyst_agent'],
        system_message="""
你是一名网络搜索代理。
你唯一的工具是search_tool——用它来查找信息。
您一次只能拨打一个搜索电话。
一旦你得到了结果，你就永远不会根据它们进行计算。
        """,
    )
    data_analyst_agent = AssistantAgent(
        "data_analyst_agent",
        description="A data analyst agent. Useful for performing calculations.",
        model_client=model_client,
        tools=[percentage_change_tool],
        handoffs=['user'],

        system_message="""
你是一名数据分析师。
鉴于您被分配的任务，您应该使用提供的工具分析数据并提供结果。 """,
    )
    text_mention_termination = TextMentionTermination("TERMINATE")
    max_messages_termination = MaxMessageTermination(max_messages=10)
    termination = text_mention_termination | max_messages_termination

    # def selector_func(messages: Sequence[AgentEvent | ChatMessage]) -> str | None:
    #     if messages[-1].source != planning_agent.name:
    #         return planning_agent.name
    #     return None

    team = Swarm(
        [planning_agent, web_search_agent, data_analyst_agent],
        termination_condition=termination,
    )
    return team


async def main():
    team = create_team()
    task = "Who was the Miami Heat player with the highest points in the 2006-2007 season?"
    await Console(team.run_stream(task=task))


asyncio.run(main())
