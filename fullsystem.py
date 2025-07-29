
import sys
from researchplanner import ResearchPlanner
from runsubagents import run_all_pending_tasks
import subprocess

def run_full_research_pipeline(topic: str, num_subtopics: int = 8):
    """
    Runs the full research pipeline: planning, subagent execution, and report generation.
    Args:
        topic (str): The research topic
        num_subtopics (int): Number of subtopics to generate (default: 8)
    """
    print(f"\n=== STEP 1: Generating research plan for: '{topic}' ===")
    planner = ResearchPlanner()
    plan = planner.create_and_save_plan(topic, num_subtopics=num_subtopics)
    if not plan:
        print("❌ Failed to generate research plan. Aborting.")
        return

    print("\n=== STEP 2: Running subagents for all pending tasks ===")
    run_all_pending_tasks()

    print("\n=== STEP 3: Generating final report ===")
    # Call report.py as a subprocess to ensure fresh environment
    result = subprocess.run([sys.executable, "report.py"], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"❌ Report generation failed: {result.stderr}")
    else:
        print("\n🎉 Research pipeline completed! Report is ready.")


if __name__ == "__main__":
    topic = "Impact of Quantum Computing on Cryptographic Security"
    num_subtopics = 10  # Default value, can be adjusted
    run_full_research_pipeline(topic, num_subtopics)
