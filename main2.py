from pickle import NONE
from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage
from langchain_core.messages import ToolMessage
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from speechtotext import speech_to_text
from texttospeech_piper import text_to_speech_live  # Using local Piper TTS for faster response
import concurrent.futures
import time

load_dotenv()


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# Define your tools here
# Example:
# @tool
# def your_tool_name(param: type):
#     """Tool description"""
#     return result

tools = []

model = ChatOllama(model="llama3.1:8b").bind_tools(tools)


def model_call(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content="""You are a helpful AI assistant. 

                        Respond naturally to user questions and engage in conversation.

                        When tools are available and the user's request requires them, use the appropriate tool.""")

    response = model.invoke([system_prompt] + state["messages"])
    return {"messages": [response]}


def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]

    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"


graph = StateGraph(AgentState)
graph.add_node("our_agent", model_call)

tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)

graph.set_entry_point("our_agent")

graph.add_conditional_edges(
    "our_agent",
    should_continue,
    {
        "continue": "tools",
        "end": END,
    }
)
graph.add_edge("tools", "our_agent")

app = graph.compile()


def run_agent(user_input: str, conversation_history: list):
    """
    Run the agent with user input and maintain conversation history
    """
    conversation_history.append(HumanMessage(content=user_input))

    inputs = {"messages": conversation_history}

    final_state = None
    for s in app.stream(inputs, stream_mode="values"):
        final_state = s

    return final_state["messages"]


def chat_loop():
    """
    Main chat loop for continuous conversation
    """
    print("=" * 60)
    print("AI Assistant Chat - use \"Go to sleep whistle!\" to end")
    print("=" * 60)
    print()

    conversation_history = []
    choice_of_text = None

    while True:
        if choice_of_text is None:
            user_input = input("press M to talk \n")
            if user_input.lower() == "m":
                user_input = speech_to_text()
                choice_of_text = False

            else:
                choice_of_text = True
        elif choice_of_text == False:
            user_input = speech_to_text()
        elif choice_of_text == True:
            user_input = input("You: ").strip()

        if user_input.lower() == "go to sleep whistle!":
            print("\nAssistant: Goodbye! Have a great day!")
            break
        if not user_input:
            continue

        try:
            conversation_history = run_agent(user_input, conversation_history)

            last_message = conversation_history[-1]
            if isinstance(last_message, AIMessage):
                response_text = last_message.content if last_message.content else "[Tool call executed]"
                print(f"\nAssistant: {response_text}\n")
                # Play the response as audio
                if response_text != "[Tool call executed]":
                    text_to_speech_live(response_text)
            else:
                response_text = last_message.content
                print(f"\nAssistant: {response_text}\n")
                # Play the response as audio
                text_to_speech_live(response_text)
            
            # # Ask user if they want to continue
            # continue_input = input("Press 'M' for speech input, Enter to continue with text, or 'Q' to quit: ").strip().lower()
            # if continue_input == 'q':
            #     print("\nAssistant: Goodbye! Have a great day!")
            #     break

        except Exception as e:
            print(f"\nError: {str(e)}\n")
            print("Please try again.\n")


if __name__ == "__main__":
    chat_loop()