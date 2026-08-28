# Verity: Autonomous Research Agent

Verity is an autonomous research agent designed to investigate complex queries using live web sources and synthesize the findings into cited research reports.

It dynamically determines when to search for new information and when to read specific webpages in depth. The system maintains a controlled research state so that final citations are based on sources successfully retrieved and processed during the investigation.

### Video Walkthrough

<!-- DRAG AND DROP YOUR RECORDED VIDEO CLIP BELOW THIS LINE -->
https://drive.google.com/file/d/1othjq-ulG-E2p5cXZkP9YDovAeM5A6rM/view?usp=drive_link
<!-- DRAG AND DROP YOUR RECORDED VIDEO CLIP ABOVE THIS LINE -->

---

### System Architecture

Verity uses a deterministic state-machine architecture designed for reliable tool use, source traceability, and controlled execution.

* **Dual-Action Routing:** The agent autonomously selects between two research tools: **Web Search** for source discovery and **Web Read** for retrieving and analyzing specific webpages.

* **Citation Traceability:** Successfully retrieved sources are stored in the research state and can be used as supporting sources in the final report. Search results that are not successfully retrieved are not treated as verified sources.

* **Graceful Error Handling:** Network failures, invalid URLs, timeouts, and empty results are captured without crashing the application. The error information is returned to the agent so it can reconsider its strategy and search for alternative sources.

* **Deterministic Step Budget:** A fixed execution limit prevents the agent from entering uncontrolled research loops. When the limit is reached, Verity stops further tool execution and synthesizes the research gathered within the available budget.

### Research Workflow

```text
User Query
    |
    v
Agent Reasoning
    |
    v
Action Router
   / \
  /   \
Search Read
  \   /
   \ /
    v
Research State
    |
    v
Synthesis
    |
    v
Cited Report
```

---

### Execution Scenarios

#### 1. Multi-Hop Research Query

**Query:**

> What are the core technical capabilities and the proposed launch timeline for NASA's Habitable Worlds Observatory?

**Verity's Behavior:**

The agent searches for relevant sources, reads specific webpages, gathers the required information, and synthesizes the findings into a cited report using the sources successfully retrieved during the research process.

**Tests:** Autonomous search, webpage reading, multi-step reasoning, source tracking, and citation generation.

---

#### 2. Error Handling Query

**Query:**

> Summarize the specific technical specifications listed on this page: https://www.nasa.gov/this-is-a-fake-404-link-test

**Verity's Behavior:**

The agent attempts to retrieve the target webpage and encounters a retrieval failure. Instead of crashing, Verity captures the error and can pivot to web search to locate relevant information from alternative accessible sources.

**Tests:** Error detection, graceful failure handling, and autonomous recovery.

---

#### 3. Step Budget Query

**Query:**

> Compile an exhaustive, day-by-day account of every technological breakthrough in artificial intelligence across all European countries from January 2020 to December 2025.

**Verity's Behavior:**

The broad query causes the agent to perform multiple research actions. Once the configured step budget is reached, Verity stops further tool execution and synthesizes the successfully gathered research context into the final report.

**Tests:** Repeated tool use, execution limits, controlled termination, and final synthesis.

---

### Installation and Deployment

1. Clone the repository:

```bash
git clone https://github.com/zainnaqvi-ai/verity-research-agent
cd Verity
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

4. Launch the application:

```bash
python interface.py
```

Do not commit `.env` or API keys to the repository.

---

### Technology Stack

| Component       | Technology            |
| --------------- | --------------------- |
| Language        | Python                |
| LLM             | Groq                  |
| Agent Framework | LangChain             |
| Orchestration   | LangGraph             |
| Web Research    | Web Search + Web Read |
| Configuration   | Python dotenv         |
| Interface       | Python                |

---

### Project Status

Verity is an active development project focused on autonomous web research, agentic tool use, source traceability, error recovery, and controlled execution.

---

### License

This project is licensed under the MIT License.

---

Developed by **Syed Ali Zain Naqvi**.
