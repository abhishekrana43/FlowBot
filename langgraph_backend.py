from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI()

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

# Checkpointer
checkpointer = InMemorySaver()

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

CONFIG = {'configurable': {'thread_id': 'thread-1'}}

# Option A: Stream message chunks (for real-time output)
print("--- Streaming response ---")
for message_chunk, metadata in chatbot.stream(
    {'messages': [HumanMessage(content='Hi my name is Abhishek Rana')]},
    config=CONFIG,
    stream_mode='messages'   # yields (chunk, metadata) tuples
):
    print(message_chunk.content, end='', flush=True)

print()  # newline after stream ends

# NOW safe to call get_state — stream has been fully consumed
print("\n--- Full state after run ---")
print(chatbot.get_state(config=CONFIG).values)


# Option B: If you just want the final output (no streaming)
# response = chatbot.invoke(
#     {'messages': [HumanMessage(content='Hi my name is Abhishek Rana')]},
#     config=CONFIG
# )
# print(response)
# print(chatbot.get_state(config=CONFIG).values)