import warnings

# Suppress all LangChain and Google SDK internal warnings
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", message=".*automatic function calling.*")

from langchain_core.messages import HumanMessage
from agent import research_agent


def execute_agent(query: str):
    print("\n" + "=" * 70)
    print("⏳ Researching... (This may take a few moments)")
    print("=" * 70)

    initial_state = {
        "messages": [HumanMessage(content=query)],
        "step_count": 0,
        "fetched_urls": []
    }

    for event in research_agent.stream(initial_state, stream_mode="values"):
        step = event.get("step_count", 0)
        last_msg = event["messages"][-1]

        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
            for tc in last_msg.tool_calls:
                print(f" ⚙️  [Step {step}] Executing Tool: {tc['name']}")
        elif last_msg.type == "tool":
            print(f" 📥 [Step {step}] Tool Data Received ({len(last_msg.content)} chars)")
        elif last_msg.type == "ai" and not getattr(last_msg, "tool_calls", None):
            print("\n" + "#" * 25 + " FINAL RESEARCH REPORT " + "#" * 25 + "\n")

            if isinstance(last_msg.content, list):
                clean_text = "".join(
                    part.get("text", "") if isinstance(part, dict) else str(part)
                    for part in last_msg.content
                )
                print(clean_text)
            else:
                print(last_msg.content)

            print("\n" + "#" * 73)


if __name__ == "__main__":
    print("Welcome to the Verity Research Agent.")
    print("Type 'exit' or 'quit' to close the program.\n")

    while True:
        user_query = input("Enter your research query: ").strip()

        if user_query.lower() in ['exit', 'quit']:
            print("Exiting Verity. Goodbye!")
            break

        if not user_query:
            continue

        execute_agent(user_query)