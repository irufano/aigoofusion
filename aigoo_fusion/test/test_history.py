import asyncio
from datetime import datetime
import pprint
import random
import time
from aigoo_fusion.chat.messages.message import Message
from aigoo_fusion.chat.messages.role import Role
from aigoo_fusion.flow.aigoo_flow import AIGooFlow
from aigoo_fusion.flow.helper.chat_memory.chat_memory import ChatMemory
from aigoo_fusion.flow.node.node import END, START
from aigoo_fusion.flow.state.workflow_state import WorkflowState


chat_memory = ChatMemory()

# Workflow
workflow = AIGooFlow({
	"messages": [] ,
})

async def main(state: WorkflowState) -> dict:
	messages = state.get("messages", [])
	responses = ["Hello", "Wowww", "Amazing", "Gokil", "Good game well played", "Selamat pagi", "Maaf aku tidak tahu"]
	random_answer = random.choice(responses)
	ai_message = Message(role=Role.ASSISTANT, content=random_answer)
	messages.append(ai_message)
	return {"messages": messages}


# Add nodes
workflow.add_node("main", main)
workflow.add_edge(START, "main")
workflow.add_edge("main", END)

async def call_workflow(question: str, thread_id: str):
	try:
		message = Message(role=Role.USER, content=question)

		async with chat_memory.intercept(thread_id=thread_id, message=message) as (messages, result_call):
			res = await workflow.execute({
				"messages": messages
			})
			# must call this back 
			result_call['messages'] = res['messages']

		history = chat_memory.get_thread_history(thread_id=thread_id, max_length=None)
		return res, history
	except Exception as e:
		raise e


async def chat_terminal():
	print("Welcome to the Chat Terminal! Type 'exit' to quit.")
	print("Use one digit number on thread id for simplicity testing, i.e: thread_id: 1")

	while True:
		thread_id = input("thread_id: ")
		user_input = input("You: ")

		if user_input.lower() == 'exit':
			print("Chatbot: Goodbye!")
			break

		response, history = await call_workflow(user_input.lower(), thread_id)
		time.sleep(0.5) # Simulate a small delay for realism
		print(f"\nChatbot: {response['messages'][-1].content}\n")
		print(f"History: ")
		for msg in history:
			print(f"\t{msg}")

if __name__ == "__main__":
	asyncio.run(chat_terminal())
