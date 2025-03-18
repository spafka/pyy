import asyncio
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_core.models import ModelFamily
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console

from myclient import model_client


# 定义工具函数
def search_web_tool(query: str) -> str:
    logging.warn("sssssss")
    """
    模拟网页搜索工具。
    :param query: 搜索查询
    :return: 搜索结果
    """
    if "2006-2007" in query:
        return """以下是迈阿密热火队球员在2006-2007赛季的总得分：
        乌杜尼斯·哈斯勒姆: 844分
        德怀恩·韦德: 1397分
        詹姆斯·波西: 550分
        ...
        """
    elif "2007-2008" in query:
        return "德怀恩·韦德在2007-2008赛季的总篮板数为214个。"
    elif "2008-2009" in query:
        return "德怀恩·韦德在2008-2009赛季的总篮板数为398个。"
    return "未找到数据。"


def percentage_change_tool(start: float, end: float) -> float:
    """
    计算百分比变化。
    :param start: 起始值
    :param end: 结束值
    :return: 百分比变化
    """
    return ((end - start) / start) * 100


# 定义LLM
import logging

from autogen_agentchat import EVENT_LOGGER_NAME, TRACE_LOGGER_NAME

logging.basicConfig(level=logging.WARNING)

# For trace logging.
trace_logger = logging.getLogger(TRACE_LOGGER_NAME)
trace_logger.addHandler(logging.StreamHandler())
trace_logger.setLevel(logging.DEBUG)

# For structured message logging, such as low-level messages between agents.
event_logger = logging.getLogger(EVENT_LOGGER_NAME)
event_logger.addHandler(logging.StreamHandler())
event_logger.setLevel(logging.DEBUG)


# 定义规划员
planning_agent = AssistantAgent(
    "planner",
    description="负责分解任务并协调团队成员。",
    model_client=model_client,
    system_message="""
    你是规划员。
    你的任务是将复杂任务分解为较小的子任务。
    你的团队成员包括：
        网页搜索员：负责搜索信息
        数据分析员：负责执行计算

    你只负责规划和分配任务，不亲自执行任务。

    分配任务时，请使用以下格式：
    1. <角色> : <任务>

    所有任务完成后，汇总结果并以“Termination”结束。
    """,
)

# 定义网页搜索员
web_search_agent = AssistantAgent(
    "web_search_agent",
    description="负责搜索信息。",
    tools=[search_web_tool],
    model_client=model_client,
    system_message="""
    你是网页搜索员。
    你唯一的工具是search_web_tool - 用它来查找信息。
    你一次只进行一次搜索调用。
    获得结果后，不要基于结果执行计算。
    """,
)

# 定义数据分析员
data_analyst_agent = AssistantAgent(
    "data_analyst_agent",
    description="负责执行计算任务。",
    model_client=model_client,
    tools=[percentage_change_tool],
    system_message="""
    你是数据分析员。
    根据分配的任务，你应该分析数据并使用提供的工具提供结果。
    """,
)

# 定义终止条件
text_mention_termination = TextMentionTermination("Termination")
max_messages_termination = MaxMessageTermination(max_messages=25)
termination = text_mention_termination | max_messages_termination

# 定义团队
team = SelectorGroupChat(
    [planning_agent, web_search_agent, data_analyst_agent],
    model_client=model_client,
    termination_condition=termination,
)

# 定义任务
task = "谁是迈阿密热火队在2006-2007赛季得分最高的球员？他在2007-2008赛季和2008-2009赛季的总篮板数之间的百分比变化是多少？"


# 运行任务
async def main() -> None:
    res=await Console(team.run_stream(task=task))
    print(res)


asyncio.run(main())
