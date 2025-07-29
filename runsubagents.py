"""
Run SubAgents Module
This module automatically checks for pending tasks in the research plan and 
runs subagents in parallel to execute research tasks.
"""

import os
import json
import time
import threading
from typing import List, Dict, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from subagent import create_research_subagent
from researchplanner import ResearchPlanner

# Configuration
MAX_CONCURRENT_THREADS = 1  # Limit concurrent threads to avoid token limits


class SubAgentRunner:
    """
    Manages the execution of multiple research subagents in parallel
    """
    
    def __init__(self, research_plan_path: str = None, max_workers: int = None):
        """
        Initialize the SubAgent Runner
        
        Args:
            research_plan_path (str): Path to research plan JSON file
            max_workers (int): Maximum number of parallel workers (defaults to MAX_CONCURRENT_THREADS)
        """
        self.research_plan_path = research_plan_path or os.path.join("Workspaces", "research_plan.json")
        self.max_workers = max_workers or MAX_CONCURRENT_THREADS
        self.planner = ResearchPlanner()
        self.task_status_lock = threading.Lock()
        self.last_known_status = {}
    
    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all pending tasks from the research plan
        
        Returns:
            List[Dict[str, Any]]: List of pending tasks
        """
        try:
            if not os.path.exists(self.research_plan_path):
                print(f"❌ Research plan file not found: {self.research_plan_path}")
                return []
            
            with open(self.research_plan_path, 'r', encoding='utf-8') as f:
                research_plan = json.load(f)
            
            pending_tasks = [
                task for task in research_plan.get("tasks", [])
                if task.get("status") == "pending"
            ]
            
            return pending_tasks
            
        except Exception as e:
            print(f"❌ Error getting pending tasks: {str(e)}")
            return []
    
    def monitor_task_status(self, task_id: str):
        """
        Monitor and print status changes for a specific task
        
        Args:
            task_id (str): The task ID to monitor
        """
        while True:
            try:
                with open(self.research_plan_path, 'r', encoding='utf-8') as f:
                    research_plan = json.load(f)
                
                # Find the task
                for task in research_plan.get("tasks", []):
                    if task.get("task_id") == task_id:
                        current_status = task.get("status")
                        
                        # Check if status changed
                        with self.task_status_lock:
                            if task_id not in self.last_known_status or self.last_known_status[task_id] != current_status:
                                self.last_known_status[task_id] = current_status
                                timestamp = datetime.now().strftime("%H:%M:%S")
                                print(f"[{timestamp}] Task {task_id}: {current_status}")
                        
                        # Stop monitoring if task is completed or failed
                        if current_status in ["completed", "failed"]:
                            return
                        
                        break
                
                # Wait before checking again
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Error monitoring task {task_id}: {str(e)}")
                time.sleep(5)
    
    def execute_task(self, task_id: str) -> Dict[str, Any]:
        """
        Execute a single research task using a subagent
        
        Args:
            task_id (str): The task ID to execute
            
        Returns:
            Dict[str, Any]: Execution result
        """
        try:
            print(f"🚀 Starting execution of Task {task_id}")
            
            # Start monitoring this task in a separate thread
            monitor_thread = threading.Thread(
                target=self.monitor_task_status,
                args=(task_id,),
                daemon=True
            )
            monitor_thread.start()
            
            # Create and execute subagent
            subagent = create_research_subagent(task_id=task_id)
            result = subagent.execute_research()
            
            return result
            
        except Exception as e:
            print(f"❌ Error executing task {task_id}: {str(e)}")
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_parallel_subagents(self) -> List[Dict[str, Any]]:
        """
        Run all pending tasks in parallel using subagents
        
        Returns:
            List[Dict[str, Any]]: List of execution results
        """
        # Get pending tasks
        pending_tasks = self.get_pending_tasks()
        
        if not pending_tasks:
            print("✅ No pending tasks found in research plan")
            return []
        
        print(f"📋 Found {len(pending_tasks)} pending tasks")
        print("🔄 Starting parallel execution of subagents...\n")
        
        # Initialize status tracking
        for task in pending_tasks:
            task_id = task.get("task_id")
            self.last_known_status[task_id] = "pending"
        
        results = []
        
        # Execute tasks in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self.execute_task, task.get("task_id")): task.get("task_id")
                for task in pending_tasks
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_task):
                task_id = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                except Exception as e:
                    print(f"❌ Task {task_id} generated an exception: {str(e)}")
                    results.append({
                        "task_id": task_id,
                        "status": "failed",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
        
        return results
    
    def display_summary(self, results: List[Dict[str, Any]]):
        """
        Display a summary of execution results
        
        Args:
            results (List[Dict[str, Any]]): List of execution results
        """
        if not results:
            return
        
        print(f"\n{'='*60}")
        print("📊 EXECUTION SUMMARY")
        print(f"{'='*60}")
        
        completed = sum(1 for r in results if r.get("status") == "completed")
        failed = sum(1 for r in results if r.get("status") == "failed")
        total = len(results)
        
        print(f"Total Tasks: {total}")
        print(f"✅ Completed: {completed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(completed/total*100):.1f}%")
        
        if failed > 0:
            print(f"\n❌ Failed Tasks:")
            for result in results:
                if result.get("status") == "failed":
                    task_id = result.get("task_id", "Unknown")
                    error = result.get("error", "Unknown error")
                    print(f"  Task {task_id}: {error}")
        
        # Show final progress
        progress = self.planner.get_plan_progress()
        print(f"\n📈 Overall Progress: {progress.get('progress_percentage', 0)}% completed")
        print(f"📝 Tasks by Status: {progress.get('tasks_by_status', {})}")
    
    def run(self):
        """
        Main execution method - runs all pending tasks in parallel
        """
        print("🔬 Research SubAgent Runner")
        print(f"📄 Using research plan: {self.research_plan_path}")
        print(f"⚡ Max parallel workers: {self.max_workers}")
        print(f"{'='*60}")
        
        # Check if research plan exists
        if not os.path.exists(self.research_plan_path):
            print(f"❌ Research plan not found: {self.research_plan_path}")
            print("💡 Please create a research plan first using researchplanner.py")
            return
        
        # Run parallel execution
        results = self.run_parallel_subagents()
        
        # Display summary
        self.display_summary(results)
        
        print(f"\n🏁 All tasks completed at {datetime.now().strftime('%H:%M:%S')}")


def run_all_pending_tasks(research_plan_path: str = None, max_workers: int = None):
    """
    Convenience function to run all pending tasks
    
    Args:
        research_plan_path (str): Path to research plan JSON file
        max_workers (int): Maximum number of parallel workers (defaults to MAX_CONCURRENT_THREADS)
    """
    runner = SubAgentRunner(research_plan_path, max_workers or MAX_CONCURRENT_THREADS)
    runner.run()


def monitor_research_progress(research_plan_path: str = None, interval: int = 10):
    """
    Monitor research progress continuously
    
    Args:
        research_plan_path (str): Path to research plan JSON file
        interval (int): Check interval in seconds
    """
    planner = ResearchPlanner()
    plan_path = research_plan_path or os.path.join("Workspaces", "research_plan.json")
    
    print("📊 Monitoring research progress...")
    print("Press Ctrl+C to stop monitoring\n")
    
    try:
        while True:
            progress = planner.get_plan_progress(plan_path)
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            print(f"[{timestamp}] Progress: {progress.get('progress_percentage', 0)}% | "
                  f"Status: {progress.get('tasks_by_status', {})}")
            
            # Check if all tasks are completed
            if progress.get('plan_status') == 'completed':
                print("🎉 All tasks completed!")
                break
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")


if __name__ == "__main__":
    # Example usage
    print("🔬 Starting Research SubAgent Runner...")
    print(f"⚡ Max concurrent threads: {MAX_CONCURRENT_THREADS}")
    
    # Run all pending tasks in parallel
    run_all_pending_tasks()
    
    # Optionally monitor progress (uncomment to use)
    # monitor_research_progress(interval=5)
