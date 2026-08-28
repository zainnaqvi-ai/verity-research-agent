import os
import warnings

warnings.filterwarnings("ignore")

from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from tools import TOOLS

load_dotenv()

MAX_STEPS = 5


def merge_unique_urls(existing: list[str], new_urls: list[str]) -> list[str]:
    return list(dict.fromkeys(existing + new_urls))


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    step_count: int
    fetched_urls: Annotated[list[str], merge_unique_urls]


llm_instance = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.1,
    api_key=os.getenv("GROQ_API_KEY")
)


def build_system_prompt(fetched_urls: list[str]) -> str:
    url_list_str = "\n".join(f"- {u}" for u in fetched_urls) if fetched_urls else "None yet."
    return (
        "You are Verity, an elite Agentic AI Researcher.\n"
        "Your mission is to answer research questions with verifiable facts and citations.\n\n"
        "Rules:\n"
        "1. Discover information using `web_search` and verify details via `fetch_page`.\n"
        "2. Ground every single claim in a verified source.\n"
        "3. TRACEABILITY REQUIREMENT: You may ONLY cite URLs that appear in the Verified Sources registry below.\n"
        "4. Format citations inline using Markdown links: [Source Title](URL).\n"
        "5. Conclude your final answer with a '### References' section listing each cited URL.\n\n"
        f"Verified Sources In Graph Memory:\n{url_list_str}"
    )


def agent_node(state: AgentState):
    llm_with_tools = llm_instance.bind_tools(TOOLS)
    system_prompt = build_system_prompt(state.get("fetched_urls", []))
    messages = [SystemMessage(content=system_prompt)] + state["messages"]

    response = llm_with_tools.invoke(messages)
    return {
        "messages": [response],
        "step_count": state.get("step_count", 0) + 1
    }


def tool_node(state: AgentState):
    last_message = state["messages"][-1]
    tool_map = {tool.name: tool for tool in TOOLS}
    tool_messages = []
    verified_urls = []

    FAILURE_MARKERS = ("HTTP error", "Failed to fetch webpage", "Webpage loaded, but no readable")

    for tool_call in getattr(last_message, "tool_calls", []):
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        if tool_name in tool_map:
            result = tool_map[tool_name].invoke(tool_args)
            if tool_name == "fetch_page" and "url" in tool_args:
                if not str(result).startswith(FAILURE_MARKERS):
                    verified_urls.append(tool_args["url"])
        else:
            result = f"Error: Tool '{tool_name}' does not exist."

        tool_messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"],
                name=tool_name
            )
        )

    return {
        "messages": tool_messages,
        "fetched_urls": verified_urls
    }


def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    step_count = state.get("step_count", 0)

    if not getattr(last_message, "tool_calls", None):
        return END

    if step_count >= MAX_STEPS:
        return "force_synthesis"

    return "tools"


def force_synthesis_node(state: AgentState):
    url_list_str = "\n".join(f"- {u}" for u in state.get("fetched_urls", []))
    fallback_prompt = HumanMessage(
        content=(
            "Step limit reached. Synthesize a complete final answer immediately using only the "
            "information gathered above. Ground every claim with inline citations and "
            f"only cite from these verified sources:\n{url_list_str}"
        )
    )
    response = llm_instance.invoke(state["messages"] + [fallback_prompt])
    return {"messages": [response]}


workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
workflow.add_node("force_synthesis", force_synthesis_node)

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "force_synthesis": "force_synthesis",
        END: END
    }
)
workflow.add_edge("tools", "agent")
workflow.add_edge("force_synthesis", END)

research_agent = workflow.compile()