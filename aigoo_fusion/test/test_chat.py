import os
from dotenv import load_dotenv

from aigoo_fusion.chat.aigoo_chat import AIGooChat
from aigoo_fusion.chat.messages.message import Message
from aigoo_fusion.chat.messages.role import Role
from aigoo_fusion.chat.models.openai.openai_config import OpenAIConfig
from aigoo_fusion.chat.models.openai.openai_model import OpenAIModel
from aigoo_fusion.chat.models.openai.openai_usage_tracker import openai_usage_tracker
from aigoo_fusion.chat.tools.tool import Tool
from aigoo_fusion.exception.aigoo_exception import AIGooException

env_file = os.getenv("ENV_FILE", ".env")  # Default to .env if ENV_FILE is not set
load_dotenv(env_file)


def _set_env(var: str):
    os.environ[var] = os.getenv(var, "None")
    # print(f"{var} set!")


_set_env("OPENAI_API_KEY")


# Test tools
def test_tools():
    # llm
    llm = OpenAIModel("gpt-4o-mini", config=OpenAIConfig(temperature=0.7))

    # Initialize framework
    framework = AIGooChat(llm, system_message="You are a helpful assistant.")

    # Define a sample tool
    @Tool()
    def get_current_weather(location: str, unit: str = "celsius") -> str:
        return f"The weather in {location} is 22 degrees {unit}"

    @Tool()
    def get_time(location: str) -> str:
        return f"The time in {location} is 09:00 AM"

    tools = [get_current_weather, get_time]

    # Register tool
    framework.register_tool(tools)

    try:
        # Example conversation with tool use
        messages = [
            Message(
                role=Role.USER,
                content="What's the weather like in London and what time?",
            )
        ]

        response = framework.generate_with_tools(messages)
        print(f"\n>> {response.result.content}\n")

    except AIGooException as e:
        print(f"Error: {e}")


# Test prompt
def test_prompt():
    info = """
	Irufano adalah seorang sofware engineer.
	Dia berasal dari Indonesia.
	"""

    # Configuration
    config = OpenAIConfig(temperature=0.7)
    llm = OpenAIModel(model="gpt-4o-mini", config=config)

    SYSTEM_PROMPT = """Answer any user questions based solely on the data below:
    <data>
    {info}
    </data>
    
    DO NOT response outside context."""

    # Initialize framework
    framework = AIGooChat(llm, system_message=SYSTEM_PROMPT, input_variables=["info"])

    try:
        # Example conversation with tool use
        messages = [Message(role=Role.USER, content="apa ibukota china")]
        with openai_usage_tracker() as usage:
            response = framework.generate(messages, info=info)
            print(f"\n>> {response.result.content}\n")
            print(f"\nUsage:\n{usage}\n")

    except AIGooException as e:
        print(f"{e}")


if __name__ == "__main__":
    # test_tools()
    test_prompt()
