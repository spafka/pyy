import asyncio
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_core.models import ModelFamily
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console

from aaa import model_client

# 定义智能体
assistant = AssistantAgent(
    "assistant",
    description="负责处理任务并返回结果。",
    model_client=model_client,
    system_message="""
    你是任务处理助手。
    你的任务是接收任务并返回处理结果。
    任务完成后，请返回“Termination”。
    """,
)

# 定义用户代理
user_proxy = UserProxyAgent(
    name="userproxy"
)

# 定义终止条件
text_mention_termination = TextMentionTermination("Termination")
max_messages_termination = MaxMessageTermination(max_messages=25)
termination = text_mention_termination | max_messages_termination

# 定义团队
team = SelectorGroupChat(
    [user_proxy, assistant],
    model_client=model_client,
    termination_condition=termination,
)

# 读取任务文件
def read_tasks(file_path: str) -> list:
    """
    从文件中读取任务。
    :param file_path: 文件路径
    :return: 任务列表
    """
    with open(file_path, "r", encoding="utf-8") as file:
        tasks = file.readlines()
    return [task.strip() for task in tasks]

# 写入结果文件
def write_results(file_path: str, results: list):
    """
    将结果写入文件。
    :param file_path: 文件路径
    :param results: 结果列表
    """
    with open(file_path, "w", encoding="utf-8") as file:
        for result in results:
            file.write(result + "\n")

# 处理任务
async def process_tasks(task_file: str, result_file: str):
    """
    逐行读取任务并提交给智能体处理。
    :param task_file: 任务文件路径
    :param result_file: 结果文件路径
    """
    tasks = read_tasks(task_file)
    results = []

    for task in tasks:
        print(f"处理任务：{task}")
        result = await Console(team.run_stream(task=task))
        results.append(result)
        print(f"任务结果：{result}")

    # 汇总结果并写入文件
    write_results(result_file, results)
    print(f"所有任务处理完成，结果已保存到 {result_file}")

# 运行程序
async def main():
    task_file = "tasks.txt"  # 任务文件路径
    result_file = "results.txt"  # 结果文件路径
    await process_tasks(task_file, result_file)

asyncio.run(main())