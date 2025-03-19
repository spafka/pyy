import asyncio
import logging

from autogen_agentchat import EVENT_LOGGER_NAME, TRACE_LOGGER_NAME
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console

from myclient import model_client

logging.basicConfig(level=logging.DEBUG)

# For trace logging.
trace_logger = logging.getLogger(TRACE_LOGGER_NAME)
trace_logger.addHandler(logging.StreamHandler())
trace_logger.setLevel(logging.DEBUG)

# For structured message logging, such as low-level messages between agents.
event_logger = logging.getLogger(EVENT_LOGGER_NAME)
event_logger.addHandler(logging.StreamHandler())
event_logger.setLevel(logging.DEBUG)


async def main() -> None:
    # 定义Agent
    primary_agent = AssistantAgent(
        name="primary",
        model_client=model_client,
        system_message="你是一个乐于助人的AI智能助手。",
        model_client_stream=False
    )

    # 定义Agent
    critic_agent = AssistantAgent(
        name="critic",
        model_client=model_client,
        system_message="提供建设性反馈意见。记住只有当你的反馈意见得到处理后再允许回复 “南哥AGI研习社”。",
        model_client_stream=False

    )

    # 定义终止条件  如果提到特定文本则终止对话
    text_termination = TextMentionTermination("南哥AGI研习社")
    # 定义终止条件，在5条信息后停止任务
    max_message_termination = MaxMessageTermination(5)
    # 使用`|` 运算符组合终止条件，在满足任一条件时停止任务
    termination = text_termination | max_message_termination

    # 定义Team Team的类型选择为RoundRobinGroupChat
    reflection_team = RoundRobinGroupChat(participants=[primary_agent, critic_agent], termination_condition=termination,
                                          max_turns=None)

    # 1、运行team并使用官方提供的Console工具以适当的格式输出
    stream = reflection_team.run_stream(task="写一首关于秋季的中文短诗")
    await Console(stream)


if __name__ == '__main__':
    # 运行main
    asyncio.run(main())
