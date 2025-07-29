
# ResearchGenie: System Architecture and Workflow

## Detailed System Workflow

**ResearchGenie** is a modular, automated research pipeline that transforms a user-supplied topic into a comprehensive, evidence-based report. The system is composed of several coordinated modules and tools, each responsible for a distinct stage of the research process. Below is a detailed explanation of how each part works and how they interact.

---

### 1. Research Planning (`researchplanner.py`)

**Purpose:**
Breaks down a broad research topic into actionable subtopics and tasks using a Large Language Model (LLM).

**How it works:**
- Receives a research topic as input.
- Uses the Gemini LLM (via LangChain) to generate a structured research plan, specifying:
  - Subtopics (tasks) with descriptive titles
  - Detailed instructions for each task
  - Key focus areas and estimated number of searches
- The plan is output as a JSON file (`Workspaces/research_plan.json`).
- Each task is initialized with a status (`pending`, `in_progress`, `completed`, `failed`).

**Key methods:**
- `generate_research_plan()`: Creates the plan using LLM prompts.
- `save_research_plan()`, `load_research_plan()`: Manage plan persistence.
- `update_task_status()`: Tracks progress of each task.

---

### 2. Subagent Execution (`runsubagents.py`, `subagent.py`)

**Purpose:**
Executes each research task in the plan, gathering and summarizing information for every subtopic.

**How it works:**
- Reads the research plan and identifies all tasks with status `pending`.
- For each task, launches a subagent (threaded for parallelism, but concurrency is limited to avoid API rate limits).
- Each subagent:
  - Performs web searches for the assigned subtopic.
  - Extracts and cleans content from relevant web pages.
  - Summarizes findings and writes results to research notes (e.g., `Workspaces/research.md`).
- Task status is updated as the subagent progresses and completes.
- The system monitors and logs the status of each task in real time.

**Key classes and functions:**
- `SubAgentRunner`: Manages parallel execution and status tracking.
- `create_research_subagent()`: Factory for subagent instances.
- `run_all_pending_tasks()`: Entry point to process all tasks.

---

### 3. Report Generation (`report.py`)

**Purpose:**
Synthesizes all research findings into a single, structured, and factual report.

**How it works:**
- Loads the completed research plan and all research notes.
- Constructs a strict, grounded prompt for the Gemini LLM, instructing it to:
  - Address every subtopic and key point from the plan
  - Use only the collected data (no hallucination)
  - Clearly indicate any gaps or uncertainties
- Streams the generated report to `Workspaces/report.md`.

**Key methods:**
- `generate()`: Loads data, builds the prompt, and writes the report.

---

### 4. Orchestration (`fullsystem.py`)

**Purpose:**
Provides a single entry point to run the entire pipeline in sequence.

**How it works:**
- Accepts a research topic (and optionally, number of subtopics) as input.
- Calls the research planner to generate the plan.
- Runs all subagents to complete the research tasks.
- Calls the report generator to synthesize the final report.
- Can be used as a function or CLI script.

**Key function:**
- `run_full_research_pipeline(topic, num_subtopics)`

---

## Tools and Supporting Modules

### Web Search (`Tools/DuckDuckGoSearch.py`)
- Provides programmatic access to DuckDuckGo search results.
- Supports HTML scraping and instant answer API.
- Used by subagents to find relevant sources.

### Web Content Extraction (`Tools/WebContentExtractor.py`)
- Uses the Trafilatura library to extract clean, readable text from web pages.
- Handles metadata extraction and fallback strategies for difficult sites.

### Unified Web Search & Extraction (`Tools/WebSearch.py`)
- Combines search and extraction for streamlined workflows.
- Allows batch processing and smart extraction strategies.

### Local File Reading (`Tools/ReadLocalFIle.py`)
- Securely reads local files (txt, json, md, csv) from the workspace.
- Used for loading research notes and plans.

---

## Data Flow Summary

1. **Input:** User provides a research topic.
2. **Planning:** LLM generates a structured plan (JSON).
3. **Task Execution:** Subagents perform web search, extraction, and summarization for each subtopic.
4. **Aggregation:** All findings are collected in research notes.
5. **Reporting:** LLM synthesizes a comprehensive report, strictly grounded in the collected data.
6. **Output:** Final report is saved as Markdown.

---

## Extending the System

- Add new tools to the `Tools/` directory for additional data sources or extraction methods.
- Customize subagent logic in `subagent.py` for domain-specific research or advanced summarization.
- Modify LLM prompts in `researchplanner.py` and `report.py` for different report styles or requirements.

---

## File Structure (Key Files)

- `fullsystem.py` — Orchestrates the full pipeline.
- `researchplanner.py` — Generates and manages research plans.
- `runsubagents.py` — Runs subagents for each research task.
- `subagent.py` — Defines subagent logic for research tasks.
- `report.py` — Synthesizes the final report.
- `Tools/` — Contains modules for web search, file reading, and content extraction.
- `Workspaces/` — Stores research plans, notes, and reports.
