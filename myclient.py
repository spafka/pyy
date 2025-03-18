from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(
    model="llama3.2",
    base_url="http://192.168.0.100:11434/v1",
    model_info={
        "function_calling": True,
        "json_output": False,
        "vision": False,
        "family": "unknown",
    }
)