# ResearchGenie

ResearchGenie is an automated research pipeline that leverages LLMs and web search to generate comprehensive, evidence-based research reports. It breaks down a research topic into actionable subtopics, runs subagents to gather and synthesize information, and produces a structured final report.

## Features
- Automated research plan generation using LLMs
- Parallel subagent execution for efficient research
- Web search and content extraction tools
- Comprehensive, grounded report generation
- Modular and extensible toolset

## Quick Start

1. **Clone the repository:**
   ```sh
   git clone https://github.com/Sachin1785/DeepResearch.git
   cd DeepResearch
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Create a `.env` file in the root directory.
   - Add your Gemini/Google API key:
     ```
     GOOGLE_API_KEY=your_api_key_here
     ```

4. **Run the full research pipeline:**
   ```sh
   python fullsystem.py
   ```
   - Edit `fullsystem.py` to change the research topic or number of subtopics.

## Project Structure

- `fullsystem.py` — Main entry point for the full research pipeline
- `researchplanner.py` — Research plan generation and management
- `runsubagents.py` — Parallel execution of research subagents
- `report.py` — Final report generation
- `Tools/` — Modular tools for web search, file reading, and content extraction
- `Workspaces/` — Stores research plans, notes, and generated reports
- `Docs/` — Documentation and tool-specific guides

## Learn More
- **General Documentation:** See [`Docs/`](Docs/) for an overview and usage instructions.
- **Tools Documentation:** See [`Docs/Tools/`](Docs/Tools/) for details on each tool.
- **Working Directory:** See [`Docs/Working/`](Docs/Working/) for workflow examples and advanced usage.
