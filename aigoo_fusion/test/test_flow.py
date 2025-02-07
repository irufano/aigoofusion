import asyncio
import os

from dotenv import load_dotenv

from aigoo_fusion.chat.aigoo_chat import AIGooChat
from aigoo_fusion.chat.messages.message import Message
from aigoo_fusion.chat.messages.role import Role
from aigoo_fusion.chat.models.openai.openai_config import OpenAIConfig
from aigoo_fusion.chat.models.openai.openai_model import OpenAIModel
from aigoo_fusion.chat.models.openai.openai_usage_tracker import openai_usage_tracker
from aigoo_fusion.chat.tools.tool import Tool
from aigoo_fusion.chat.tools.tool_registry import ToolRegistry
from aigoo_fusion.flow.aigoo_flow import AIGooFlow
from aigoo_fusion.flow.helper.tools_node.tools_node import tools_node
from aigoo_fusion.flow.node.node import END, START
from aigoo_fusion.flow.state.workflow_state import WorkflowState

env_file = os.getenv("ENV_FILE", ".env")  # Default to .env if ENV_FILE is not set
load_dotenv(env_file)


def _set_env(var: str):
    os.environ[var] = os.getenv(var, "None")
    # print(f"{var} set!")


_set_env("OPENAI_API_KEY")


async def test_workflow():
    # Create workflow with initial state
    workflow = AIGooFlow(
        {
            "config": {"max_length": 20, "min_length": 10, "model": "gpt-4"},
        }
    )

    # Define processing functions
    async def process_input(text: str, state: WorkflowState) -> dict:
        return {"processed_input": text.upper()}

    async def handle_long_text(processed_input: str, state: WorkflowState) -> dict:
        return {"result": f"Handled long text: {processed_input[:20]}..."}

    async def handle_short_text(processed_input: str, state: WorkflowState) -> dict:
        return {"result": f"Handled short text: {processed_input}"}

    async def handle_medium_text(processed_input: str, state: WorkflowState) -> dict:
        return {"result": f"Handled medium text: {processed_input}"}

    # Define routing condition
    def route_by_length(state: WorkflowState) -> str:
        text = state.get("processed_input", "")
        config = state.get("config", {})
        max_length = config.get("max_length", 20)
        min_length = config.get("min_length", 10)

        if len(text) > max_length:
            return "handle_long"
        elif len(text) < min_length:
            return "handle_short"
        elif len(text) == 0:
            return "END"
        else:
            return "handle_medium"

    # Add nodes
    workflow.add_node("process", process_input)
    workflow.add_node("handle_long", handle_long_text)
    workflow.add_node("handle_short", handle_short_text)
    workflow.add_node("handle_medium", handle_medium_text)

    workflow.add_edge(START, "process")

    # Add conditional edge with multiple possible destinations
    workflow.add_conditional_edge(
        "process", ["handle_long", "handle_short", "handle_medium"], route_by_length
    )

    workflow.add_edge("handle_long", END)
    workflow.add_edge("handle_short", END)
    workflow.add_edge("handle_medium", END)

    diagram = workflow.get_diagram_url()

    # Test with different inputs
    results = []
    for text in [
        "Short",
        "This is a very long text that exceeds the maximum length",
        "Medium text",
    ]:
        result = await workflow.execute({"text": text})
        results.append(result)
        print(result)
        print(diagram)

    return results


# Test with aigoochat
async def test_aigoochat():
    # Configuration
    config = OpenAIConfig(temperature=0.7)

    llm = OpenAIModel("gpt-4o-mini", config)

    # Define a sample tool
    @Tool()
    def get_current_weather(location: str, unit: str = "celsius") -> str:
        return f"The weather in {location} is 22 degrees {unit}"

    @Tool()
    def get_current_time(location: str) -> str:
        # Initialize framework
        aig = AIGooChat(llm, system_message="You are a helpful assistant.")

        # Example conversation with tool use
        time = f"The time in {location} is 09:00 AM"
        msgs = [
            Message(role=Role.USER, content=time),
        ]
        res = aig.generate(msgs)
        return res.result.content or "No data"

    tool_list = [get_current_weather, get_current_time]

    # Initialize framework
    fmk = AIGooChat(llm, system_message="You are a helpful assistant.")

    # Register tool
    fmk.register_tool(tool_list)

    # Register to ToolRegistry
    tl_registry = ToolRegistry(tool_list)

    # Workflow
    workflow = AIGooFlow(
        {
            "messages": [],
        }
    )

    async def main_agent(state: WorkflowState) -> dict:
        messages = state.get("messages", [])
        response = fmk.generate(messages)
        messages.append(response.process[-1])
        return {"messages": messages, "system": response.process[0]}

    async def tools(state: WorkflowState) -> dict:
        messages = tools_node(messages=state.get("messages", []), registry=tl_registry)
        return {"messages": messages}

    def should_continue(state: WorkflowState) -> str:
        messages = state.get("messages", [])
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END

    # Add nodes
    workflow.add_node("main_agent", main_agent)
    workflow.add_node("tools", tools)

    # Define workflow structure
    workflow.add_edge(START, "main_agent")
    workflow.add_conditional_edge("main_agent", ["tools", END], should_continue)
    workflow.add_edge("tools", "main_agent")

    async def call_sql_agent(question: str):
        try:
            with openai_usage_tracker() as usage:
                res = await workflow.execute(
                    {
                        "messages": [
                            # Message(role=Role.USER, content="Siapa suksesor untuk posisi Chief Technology Officer?")
                            Message(role=Role.USER, content=question)
                        ]
                    }
                )

            return res, usage
        except Exception as e:
            raise e

    quest = "What's the weather like in London and what time is it?"
    res, usage = await call_sql_agent(quest)
    print("---\nResponse content:\n")
    print(res["messages"][-1].content)
    print("---\nRaw usages:")
    for usg in usage.raw_usages:
        print(f"{usg}")
    print(f"---\nCallback:\n {usage}")


async def run():
    # await test_aigoochat()
    await test_workflow()


asyncio.run(run())
