import os
import webbrowser
import threading
import warnings

warnings.filterwarnings("ignore")

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from agent import research_agent

app = FastAPI(title="Verity 1.0 Interface")

# Serve the static frontend folder
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


class ResearchRequest(BaseModel):
    query: str


@app.get("/")
def get_index():
    return FileResponse("static/index.html")


@app.post("/api/research")
def run_research_endpoint(req: ResearchRequest):
    initial_state = {
        "messages": [HumanMessage(content=req.query)],
        "step_count": 0,
        "fetched_urls": []
    }

    final_text = "No report generated."
    verified_sources = []

    try:
        for event in research_agent.stream(initial_state, stream_mode="values"):
            # Programmatically track the exact URLs the agent successfully read
            if "fetched_urls" in event:
                verified_sources = event["fetched_urls"]

            last_msg = event["messages"][-1]
            if last_msg.type == "ai" and not getattr(last_msg, "tool_calls", None):
                if isinstance(last_msg.content, list):
                    final_text = "".join(
                        part.get("text", "") if isinstance(part, dict) else str(part)
                        for part in last_msg.content
                    )
                else:
                    final_text = str(last_msg.content)

        return {"report": final_text, "sources": verified_sources}
    except Exception as e:
        return {"error": str(e)}


def open_browser():
    webbrowser.open("http://127.0.0.1:8000")


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting VERITY 1.0 Fullstack Interface...")
    print("🌐 Web UI available at: http://127.0.0.1:8000")
    print("=" * 60)
    threading.Timer(1.2, open_browser).start()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")