import sys
from researchplanner import ResearchPlanner
from runsubagents import run_all_pending_tasks
import subprocess

# Colorful print helpers
def log_info(msg):
    print(f"\033[94m[INFO]\033[0m {msg}")

def log_success(msg):
    print(f"\033[92m[SUCCESS]\033[0m {msg}")

def log_warning(msg):
    print(f"\033[93m[WARNING]\033[0m {msg}")

def log_error(msg):
    print(f"\033[91m[ERROR]\033[0m {msg}")

def log_stage(msg):
    print(f"\033[96m[STAGE]\033[0m {msg}")

def run_full_research_pipeline(topic: str, num_subtopics: int = 8):
    """
    Runs the full research pipeline: planning, subagent execution, and report generation.
    Args:
        topic (str): The research topic
        num_subtopics (int): Number of subtopics to generate (default: 8)
    """
    log_stage(f"STEP 1: Generating research plan for: '{topic}'")
    planner = ResearchPlanner()
    plan = planner.create_and_save_plan(topic, num_subtopics=num_subtopics)
    if not plan:
        log_error("Failed to generate research plan. Aborting.")
        return

    log_stage("STEP 2: Running subagents for all pending tasks")
    run_all_pending_tasks()

    log_stage("STEP 3: Generating final report")
    # Call report.py as a subprocess to ensure fresh environment
    result = subprocess.run([sys.executable, "report.py"], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        log_error(f"Report generation failed: {result.stderr}")
    else:
        log_success("\n🎉 Research pipeline completed! Report is ready.")


if __name__ == "__main__":
    topic = "Provide a report on the long-term trends in ocean acidification in the North Atlantic. The report should summarize key findings, analyze the relationships between pH and salinity, and automatically generate a summary suitable for a policy brief"
    num_subtopics = 10  # Default value, can be adjusted
    run_full_research_pipeline(topic, num_subtopics)
