# To run this code you need to install the following dependencies:
# pip install google-genai

import os
import json
from google import genai
from google.genai import types


def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def generate():
    # Load research plan and research.md
    plan = json.loads(load_file("Workspaces/research_plan.json"))
    research_md = load_file("Workspaces/research.md")

    # Build the strict and grounded system prompt
    prompt = f"""
You are an expert research analyst using the Gemini thinking model with access to search-based grounding.

Your task:
- Write a comprehensive, structured, and factual report on:
  "{plan['research_topic']}"

Strict rules you MUST follow:
- Do **not fabricate or hallucinate** any facts, statistics, sources, or claims.
- Use only information from the research plan and research.md.
- If a point is unclear or unsupported by the given data, **search and ground your answer using real sources**.
- If something cannot be confirmed or validated, explicitly state that.
- Ensure **every subtopic, bullet, and key point** in the research plan is fully addressed — do not skip anything.
- Organize the report clearly with sections and subsections where needed.
- Be specific, evidence-based, and mention important trends, problems, or findings.

Research Plan:
{json.dumps(plan, indent=2)}

Research Notes (Markdown):
{research_md}

Now generate the full report below:
"""

    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0.4,
        thinking_config=types.ThinkingConfig(
            thinking_budget=-1,
        ),
    )

    output_path = "Workspaces/report.md"
    with open(output_path, "w", encoding="utf-8") as output_file:
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            output_file.write(chunk.text)

    print(f"\n✅ Report saved to {output_path}")


if __name__ == "__main__":
    generate()
