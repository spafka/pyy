import logging

from autogen_agentchat import TRACE_LOGGER_NAME, EVENT_LOGGER_NAME
from autogen_ext.models.openai import OpenAIChatCompletionClient

# logging.basicConfig(level=logging.DEBUG)
#
# # For trace logging.
# trace_logger = logging.getLogger(TRACE_LOGGER_NAME)
# trace_logger.addHandler(logging.StreamHandler())
# trace_logger.setLevel(logging.DEBUG)

# For structured message logging, such as low-level messages between agents.
# event_logger = logging.getLogger(EVENT_LOGGER_NAME)
# event_logger.addHandler(logging.StreamHandler())
# event_logger.setLevel(logging.DEBUG)
model_client = OpenAIChatCompletionClient(
    model="llama3.2",
    base_url="http://192.168.0.100:11434/v1",
    model_info={
        "function_calling": True,
        "json_output": False,
        "vision": False,
        "stream": False,
        "family": "unknown",
    }
)