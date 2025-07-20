"""
Research Planner Module
This module generates structured research plans using LLM and stores them in JSON format.
It breaks down research topics into specific subtopics and tasks for sub-agents to execute.
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()


class ResearchPlanner:
    """
    A research planner that generates structured research plans using LLM
    and manages the research planning workflow.
    """
    
    def __init__(self, gemini_api_key: str = None, model_name: str = "gemini-2.0-flash-lite"):
        """
        Initialize the research planner
        
        Args:
            gemini_api_key (str): API key for Gemini (if not set in environment)
            model_name (str): Gemini model to use
        """
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
            temperature=0.2,  # Lower temperature for more structured output
            max_tokens=4096   # Higher token limit for detailed plans
        )
    
    def generate_research_plan(self, research_topic: str, num_subtopics: int = 8) -> Optional[Dict[str, Any]]:
        """
        Generate a comprehensive research plan for the given topic
        
        Args:
            research_topic (str): The main research topic
            num_subtopics (int): Number of subtopics to generate (default: 8)
        
        Returns:
            Optional[Dict[str, Any]]: Research plan in JSON format or None if failed
        """
        try:
            # Create the prompt for research plan generation
            prompt = self._create_research_plan_prompt(research_topic, num_subtopics)
            
            # Generate the research plan
            response = self.llm.invoke(prompt)
            
            # Parse the response to extract JSON
            plan_json = self._extract_json_from_response(response.content)
            
            if plan_json:
                # Add metadata
                plan_json["research_topic"] = research_topic
                plan_json["plan_created"] = datetime.now().isoformat()
                plan_json["plan_status"] = "active"
                
                return plan_json
            else:
                print(f"Error: Could not parse research plan from LLM response")
                return None
                
        except Exception as e:
            print(f"Error generating research plan: {str(e)}")
            return None
    
    def _create_research_plan_prompt(self, research_topic: str, num_subtopics: int) -> str:
        """Create the prompt for research plan generation"""
        return f"""You are an expert research planner. Create a comprehensive research plan for the topic: "{research_topic}"

TASK: Generate a structured research plan with {num_subtopics} distinct subtopics/tasks that cover all major aspects of this research topic.

REQUIREMENTS:
1. Each subtopic should be specific and focused
2. Cover different angles: technical, historical, current state, future trends, applications, challenges
3. Include both broad overview topics and deep-dive specific areas
4. Ensure comprehensive coverage of the research topic
5. Make each task actionable for a research agent

OUTPUT FORMAT: Respond ONLY with a valid JSON object in this exact structure:

{{
  "tasks": [
    {{
      "task_id": "1",
      "subtopic": "Brief descriptive title of the subtopic",
      "description": "Detailed description of what to research and focus on",
      "estimated_searches": 5,
      "key_areas": ["area1", "area2", "area3"],
      "status": "pending"
    }},
    {{
      "task_id": "2",
      "subtopic": "Another subtopic title",
      "description": "Another detailed description",
      "estimated_searches": 4,
      "key_areas": ["area1", "area2"],
      "status": "pending"
    }}
  ]
}}

IMPORTANT GUIDELINES:
- Make each subtopic distinct and non-overlapping
- Estimated_searches should be 3-8 per task
- Key_areas should be 2-5 specific focus areas per task
- Descriptions should be 50-100 words and very specific
- Ensure the JSON is valid and properly formatted

Generate the research plan now:"""
    
    def _extract_json_from_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Extract and parse JSON from LLM response"""
        try:
            # Try to find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                print("No JSON found in response")
                return None
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            return None
        except Exception as e:
            print(f"Error extracting JSON: {str(e)}")
            return None
    
    def save_research_plan(self, research_plan: Dict[str, Any], file_path: str = None) -> bool:
        """
        Save the research plan to a JSON file
        
        Args:
            research_plan (Dict[str, Any]): The research plan to save
            file_path (str): Optional custom file path
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            if file_path is None:
                file_path = os.path.join("Workspaces", "research_plan.json")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(research_plan, f, indent=2, ensure_ascii=False)
            
            print(f"Research plan saved to: {file_path}")
            return True
            
        except Exception as e:
            print(f"Error saving research plan: {str(e)}")
            return False
    
    def load_research_plan(self, file_path: str = None) -> Optional[Dict[str, Any]]:
        """
        Load a research plan from a JSON file
        
        Args:
            file_path (str): Optional custom file path
        
        Returns:
            Optional[Dict[str, Any]]: Research plan or None if failed
        """
        try:
            if file_path is None:
                file_path = os.path.join("Workspaces", "research_plan.json")
            
            if not os.path.exists(file_path):
                print(f"Research plan file not found: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                research_plan = json.load(f)
            
            return research_plan
            
        except Exception as e:
            print(f"Error loading research plan: {str(e)}")
            return None
    
    def update_task_status(self, task_id: str, status: str, file_path: str = None) -> bool:
        """
        Update the status of a specific task in the research plan
        
        Args:
            task_id (str): ID of the task to update
            status (str): New status ("pending", "in_progress", "completed", "failed")
            file_path (str): Optional custom file path
        
        Returns:
            bool: True if updated successfully, False otherwise
        """
        try:
            # Load current plan
            research_plan = self.load_research_plan(file_path)
            if not research_plan:
                return False
            
            # Find and update the task
            task_found = False
            for task in research_plan.get("tasks", []):
                if task.get("task_id") == task_id:
                    task["status"] = status
                    task["last_updated"] = datetime.now().isoformat()
                    task_found = True
                    break
            
            if not task_found:
                print(f"Task with ID {task_id} not found")
                return False
            
            # Update metadata
            completed_tasks = sum(1 for task in research_plan.get("tasks", []) if task.get("status") == "completed")
            research_plan["last_updated"] = datetime.now().isoformat()
            
            # Check if all tasks are completed
            total_tasks = len(research_plan.get("tasks", []))
            if completed_tasks == total_tasks:
                research_plan["plan_status"] = "completed"
            
            # Save updated plan
            return self.save_research_plan(research_plan, file_path)
            
        except Exception as e:
            print(f"Error updating task status: {str(e)}")
            return False
    
    def get_pending_tasks(self, file_path: str = None) -> List[Dict[str, Any]]:
        """
        Get all pending tasks from the research plan
        
        Args:
            file_path (str): Optional custom file path
        
        Returns:
            List[Dict[str, Any]]: List of pending tasks
        """
        try:
            research_plan = self.load_research_plan(file_path)
            if not research_plan:
                return []
            
            pending_tasks = [
                task for task in research_plan.get("tasks", [])
                if task.get("status") == "pending"
            ]
            
            return pending_tasks
            
        except Exception as e:
            print(f"Error getting pending tasks: {str(e)}")
            return []
    
    def get_plan_progress(self, file_path: str = None) -> Dict[str, Any]:
        """
        Get the current progress of the research plan
        
        Args:
            file_path (str): Optional custom file path
        
        Returns:
            Dict[str, Any]: Progress information
        """
        try:
            research_plan = self.load_research_plan(file_path)
            if not research_plan:
                return {}
            
            tasks = research_plan.get("tasks", [])
            total_tasks = len(tasks)
            completed_tasks = sum(1 for task in tasks if task.get("status") == "completed")
            progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            tasks_by_status = {}
            for task in tasks:
                status = task.get("status", "unknown")
                tasks_by_status[status] = tasks_by_status.get(status, 0) + 1
            
            return {
                "research_topic": research_plan.get("research_topic", ""),
                "plan_status": research_plan.get("plan_status", "unknown"),
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "progress_percentage": round(progress_percentage, 2),
                "tasks_by_status": tasks_by_status,
                "plan_created": research_plan.get("plan_created", ""),
                "last_updated": research_plan.get("last_updated", "")
            }
            
        except Exception as e:
            print(f"Error getting plan progress: {str(e)}")
            return {}
    
    def create_and_save_plan(self, research_topic: str, num_subtopics: int = 8, file_path: str = None) -> Optional[Dict[str, Any]]:
        """
        Convenience method to generate and save a research plan in one step
        
        Args:
            research_topic (str): The main research topic
            num_subtopics (int): Number of subtopics to generate
            file_path (str): Optional custom file path
        
        Returns:
            Optional[Dict[str, Any]]: Research plan or None if failed
        """
        # Generate the plan
        research_plan = self.generate_research_plan(research_topic, num_subtopics)
        
        if research_plan:
            # Save the plan
            if self.save_research_plan(research_plan, file_path):
                print(f"✅ Research plan created and saved successfully!")
                print(f"📊 Generated {len(research_plan.get('tasks', []))} research tasks")
                return research_plan
            else:
                print("❌ Failed to save research plan")
                return None
        else:
            print("❌ Failed to generate research plan")
            return None


# Convenience functions
def create_research_plan(research_topic: str, num_subtopics: int = 8) -> Optional[Dict[str, Any]]:
    """
    Convenience function to create a research plan
    
    Args:
        research_topic (str): The main research topic
        num_subtopics (int): Number of subtopics to generate
    
    Returns:
        Optional[Dict[str, Any]]: Research plan or None if failed
    """
    planner = ResearchPlanner()
    return planner.create_and_save_plan(research_topic, num_subtopics)


def get_plan_status(file_path: str = None) -> Dict[str, Any]:
    """
    Convenience function to get plan progress
    
    Args:
        file_path (str): Optional custom file path
    
    Returns:
        Dict[str, Any]: Progress information
    """
    planner = ResearchPlanner()
    return planner.get_plan_progress(file_path)


def mark_task_completed(task_id: str, file_path: str = None) -> bool:
    """
    Convenience function to mark a task as completed
    
    Args:
        task_id (str): ID of the task to complete
        file_path (str): Optional custom file path
    
    Returns:
        bool: True if updated successfully, False otherwise
    """
    planner = ResearchPlanner()
    return planner.update_task_status(task_id, "completed", file_path)


# Example usage
if __name__ == "__main__":
    # Example of creating a research plan
    planner = ResearchPlanner()
    
    # Create a research plan
    topic = "AI applications in healthcare diagnosis and treatment"
    plan = planner.create_and_save_plan(topic, num_subtopics=6)
    
    if plan:
        print("Plan created.")
