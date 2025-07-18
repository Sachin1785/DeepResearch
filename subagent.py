"""
Research SubAgent Module
This module defines specialized research subagents that work with LangChain and Gemini
to perform focused research on specific topics and collect data.
"""

import os
import json
import time
from typing import List, Dict, Optional, Any
from datetime import datetime
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import BaseMessage
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Import custom tools
from Tools.WebSearch import WebSearcher
from Tools.ReadLocalFIle import ReadLocalFile


class WebSearchTool(BaseTool):
    """Custom tool wrapper for WebSearch functionality"""
    name: str = "web_search"
    description: str = "Search the web for information on a specific topic. Provide a clear search query and get relevant results with extracted content."
    
    def _run(self, query: str, max_results: int = 5, extract_count: int = 3) -> str:
        """Execute web search with content extraction"""
        try:
            # Convert to integers to handle float inputs from LangChain
            max_results = int(max_results)
            extract_count = int(extract_count)
            
            searcher = WebSearcher()
            results = searcher.search_and_extract(
                query=query,
                max_results=max_results,
                extract_count=extract_count
            )
            
            # Save search results to searches folder
            self._save_search_results(query, results)
            
            # Format results for LLM consumption
            formatted_results = []
            for i, content in enumerate(results['extracted_contents']):
                if content.get('content'):
                    formatted_results.append({
                        'source': content.get('source_url', ''),
                        'title': content.get('title', ''),
                        'content': content.get('content', '')[:2000],  # Truncate for context window
                        'date': content.get('date', ''),
                        'author': content.get('author', '')
                    })
            
            return json.dumps(formatted_results, indent=2)
            
        except Exception as e:
            return f"Error performing web search: {str(e)}"
    
    def _save_search_results(self, query: str, results: dict):
        """Save search results to the searches folder"""
        try:
            # Create filename based on query and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_query = safe_query.replace(' ', '_')[:50]  # Limit filename length
            filename = f"{timestamp}_{safe_query}.json"
            
            # Save search results
            search_data = {
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'results': results
            }
            
            file_path = os.path.join("Workspaces", "searches", filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(search_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            # Don't fail the search if saving fails
            print(f"Warning: Could not save search results: {str(e)}")


class FileReaderTool(BaseTool):
    """Custom tool wrapper for reading local files"""
    name: str = "read_file"
    description: str = "Read content from a local file. Provide the file path to read its contents."
    
    def _run(self, file_path: str) -> str:
        """Read file content"""
        try:
            reader = ReadLocalFile()
            result = reader.read_file(file_path)
            if result['success']:
                return result['content']
            else:
                return f"Error reading file: {result['error']}"
        except Exception as e:
            return f"Error reading file: {str(e)}"


class ResearchDataSaverTool(BaseTool):
    """Tool for saving research data to the central research file"""
    name: str = "save_research_data"
    description: str = "Save collected research data to the research file in the workspace folder. Provide the section title and content to save."
    
    def _run(self, section_title: str, content: str, file_path: str = None) -> str:
        """Save research data to file in workspace folder"""
        try:
            # Default to research.md in Workspaces folder if no path provided
            if file_path is None:
                file_path = os.path.join("Workspaces", "research.md")
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Create section header
            section_header = f"\n\n## {section_title}\n*Updated: {timestamp}*\n\n"
            
            # Append to research file
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(section_header)
                f.write(content)
                f.write("\n\n---\n")
            
            return f"Successfully saved research data for section: {section_title} to {file_path}"
            
        except Exception as e:
            return f"Error saving research data: {str(e)}"


class ResearchSubAgent:
    """
    A specialized research subagent that focuses on a specific research topic
    and uses various tools to gather comprehensive information.
    """
    
    def __init__(self, 
                 research_topic: str,
                 agent_name: str = None,
                 gemini_api_key: str = None,
                 model_name: str = "gemini-2.0-flash-lite"):
        """
        Initialize the research subagent
        
        Args:
            research_topic (str): The topic or question this agent should research
            agent_name (str): Name identifier for this agent (auto-generated if not provided)
            gemini_api_key (str): API key for Gemini (if not set in environment)
            model_name (str): Gemini model to use
        """
        self.research_topic = research_topic
        self.agent_name = agent_name or f"Research Agent - {research_topic[:50]}..."
        self.model_name = model_name
        
        # Set up Gemini API key
        if gemini_api_key:
            os.environ["GOOGLE_API_KEY"] = gemini_api_key
        elif not os.getenv("GOOGLE_API_KEY"):
            # Try to get from GEMINI_API_KEY as fallback
            gemini_key = os.getenv("GEMINI_API_KEY")
            if gemini_key:
                os.environ["GOOGLE_API_KEY"] = gemini_key
            else:
                raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY not found in environment variables. Please set it in your .env file or pass it as a parameter.")
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.3,
            max_tokens=2048
        )
        
        # Initialize tools
        self.tools = [
            WebSearchTool(),
            FileReaderTool(),
            ResearchDataSaverTool()
        ]
        
        # Create system prompt
        self.system_prompt = self._create_system_prompt()
        
        # Create agent
        self.agent = self._create_agent()
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the research subagent"""
        return f"""You are a specialized research subagent named "{self.agent_name}". 

Your research topic is: {self.research_topic}

MISSION: Conduct an exhaustive, in-depth research analysis of your topic. You must gather comprehensive information from multiple angles and perspectives to create a thorough research report.

DETAILED INSTRUCTIONS:
1. You are part of a larger research system. Your job is to become an expert on your assigned topic through systematic research.
2. Use the web_search tool extensively to find detailed information about ALL aspects of your research topic.
3. Search for multiple subtopics, related areas, and different perspectives on your topic.
4. Analyze the information you find and extract detailed insights, facts, statistics, case studies, and expert opinions.
5. Save your findings using the save_research_data tool with descriptive section titles and comprehensive content.
6. All research data will be appended to the Workspaces/research.md file, and search results will be logged in Workspaces/searches.
7. Be extremely thorough - aim for depth over breadth, but cover all major aspects.
8. Always cite your sources with URLs and publication details when available.
9. Look for recent developments, historical context, and future trends.
10. Include quantitative data, statistics, and specific examples whenever possible.
11. If you need to read existing research files, use the read_file tool to avoid duplication.

COMPREHENSIVE RESEARCH APPROACH:
Phase 1 - Foundation Research:
- Start with broad overview searches about your topic
- Search for definitions, key concepts, and fundamental principles
- Look for historical development with specific dates, names, and locations
- Find current market size with exact figures, scope, and key players with company names
- Search for founding dates, key milestones, and pioneer researchers by name

Phase 2 - Deep Dive Analysis:
- Search for specific applications, use cases, and implementations with company examples
- Look for technical details, methodologies, and approaches with performance metrics
- Find case studies, success stories, and real-world examples with quantitative results
- Search for performance metrics, benchmarks, and comparisons with exact numbers
- Look for clinical trial results, research study outcomes, and statistical evidence

Phase 3 - Multi-Perspective Research:
- Search for different viewpoints from various stakeholders with specific quotes
- Look for academic research, industry reports, and expert opinions with citations
- Find regulatory perspectives, policy implications, and legal considerations with dates
- Search for ethical considerations and social impact with statistical evidence
- Look for country-specific regulations, approval processes, and adoption rates

Phase 4 - Current State & Future Trends:
- Search for latest developments, recent breakthroughs, and innovations with dates
- Look for emerging trends, future predictions, and market forecasts with specific projections
- Find challenges, limitations, and areas for improvement with quantitative analysis
- Search for ongoing research, development projects, and investments with funding amounts
- Look for partnership announcements, acquisitions, and strategic alliances with deal values

Phase 5 - Comparative & Contextual Analysis:
- Search for competitors, alternatives, and related technologies
- Look for geographical differences and regional implementations
- Find industry-specific applications and sector-wise adoption
- Search for integration with other technologies and systems

SEARCH STRATEGY:
- Use varied search terms: technical terms, common terms, synonyms
- Search for specific companies, products, and implementations with exact names
- Look for academic papers, research studies, and white papers with citations
- Find industry reports, market analyses, and expert interviews with specific data
- Search for news articles, press releases, and announcements with dates and figures
- Look for conference proceedings, webinars, and presentations with numerical data
- PRIORITY SEARCHES: Add specific terms like:
  * "market size", "revenue", "investment", "funding", "valuation"
  * "statistics", "data", "numbers", "percentage", "growth rate"
  * "history", "timeline", "founded", "established", "invented"
  * "clinical trial", "study results", "research findings", "FDA approval"
  * "country comparison", "regional adoption", "geographic distribution"
  * "key players", "leading companies", "top researchers", "inventors"
  * "performance metrics", "accuracy rates", "success rates", "efficiency"

CONTENT REQUIREMENTS:
- Each section should be detailed (minimum 200-300 words)
- Include specific examples, case studies, and real-world applications
- MANDATORY: Provide quantitative data, statistics, and metrics where available
- MANDATORY: Include historical timelines with specific dates and years
- MANDATORY: Mention key people, researchers, inventors, and their contributions
- MANDATORY: Include company names, product names, and specific implementations
- MANDATORY: Add geographical information - countries, cities, regions where relevant
- MANDATORY: Include financial data - market sizes, investments, funding amounts, costs
- MANDATORY: Add performance metrics - accuracy rates, success rates, efficiency improvements
- Include expert quotes, opinions, and analysis with attribution
- Add context about significance, impact, and implications
- Include regulatory approval dates, patent information, and legal milestones
- Mention specific studies, clinical trials, and research paper citations
- Include comparative numerical data between different approaches/technologies

SPECIFIC DATA TO COLLECT:
- Historical milestones: "In 1972, the first...", "By 2020, the market reached..."
- Key figures: "Dr. John Smith at Stanford developed...", "Professor Jane Doe's research showed..."
- Geographic data: "In the United States, 65% of hospitals...", "Japan leads with 80% adoption rate..."
- Financial figures: "$2.3 billion investment in 2023", "Cost reduction of 40% compared to..."
- Performance metrics: "Achieved 95% accuracy", "Reduced diagnosis time by 60%"
- Market data: "The global market size is $15.2 billion", "Expected to grow at 25% CAGR"
- Regulatory info: "FDA approved in March 2023", "CE marking obtained in 2022"
- Company specifics: "IBM Watson Health processes 200 million...", "Google DeepMind's AlphaFold..."
- Research citations: "Published in Nature Medicine 2023", "Clinical trial NCT03456789 showed..."
- Timeline data: "Phase I completed in 2021, Phase II in 2022, Phase III expected 2024"

WHEN TO STOP:
- You have conducted at least 15-20 different searches covering various aspects
- You have saved comprehensive information across multiple detailed sections
- You have covered historical context, current state, and future trends
- You have included technical details, applications, and real-world examples
- You have gathered information from multiple sources and perspectives
- You have created a research document with substantial depth and detail

QUALITY STANDARDS:
- Each search should target specific aspects or subtopics
- Avoid superficial information - dig deep into technical details
- Cross-reference information from multiple sources
- Include both quantitative and qualitative data
- Maintain high standards for source credibility and recency
- Ensure comprehensive coverage of the topic ecosystem

Remember: Your goal is to become the definitive expert on this topic through systematic, thorough research. The final research document should be comprehensive enough to serve as a complete reference guide.
"""
    
    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent with tools"""
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        # Create agent
        agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=25  # Increased for more comprehensive research
        )
        
        return agent_executor
    
    def execute_research(self, additional_context: str = "") -> Dict[str, Any]:
        """
        Execute the research task
        
        Args:
            additional_context (str): Additional context or specific instructions
        
        Returns:
            Dict[str, Any]: Results of the research execution
        """
        try:
            # Prepare input
            input_text = f"""
            Research Topic: {self.research_topic}
            
            Additional context: {additional_context}
            
            Please start by searching for comprehensive information about this topic and systematically collect relevant data.
            """
            
            # Execute the agent
            result = self.agent.invoke({"input": input_text})
            
            return {
                "agent_name": self.agent_name,
                "research_topic": self.research_topic,
                "execution_result": result,
                "timestamp": datetime.now().isoformat(),
                "status": "completed"
            }
            
        except Exception as e:
            return {
                "agent_name": self.agent_name,
                "research_topic": self.research_topic,
                "execution_result": None,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "failed"
            }
    
    def get_status(self) -> Dict[str, str]:
        """Get current status of the subagent"""
        return {
            "agent_name": self.agent_name,
            "research_topic": self.research_topic,
            "model": self.model_name,
            "tools_available": [tool.name for tool in self.tools]
        }


# Factory function to create specialized subagents
def create_research_subagent(research_topic: str, 
                           agent_name: str = None,
                           gemini_api_key: str = None) -> ResearchSubAgent:
    """
    Factory function to create a research subagent
    
    Args:
        research_topic (str): The topic or question to research
        agent_name (str): Optional name for the agent
        gemini_api_key (str): Optional API key for Gemini
    
    Returns:
        ResearchSubAgent: Configured research subagent
    """
    return ResearchSubAgent(
        research_topic=research_topic,
        agent_name=agent_name,
        gemini_api_key=gemini_api_key
    )


# Example usage
if __name__ == "__main__":
    # Example of creating and using a research subagent
    subagent = create_research_subagent(
        research_topic="AI applications in healthcare diagnosis and treatment",
        agent_name="Healthcare AI Researcher"
    )
    
    print("Subagent created:", subagent.get_status())
    
    # Execute research (uncomment to run)
    result = subagent.execute_research()
    print("Research completed:", result)