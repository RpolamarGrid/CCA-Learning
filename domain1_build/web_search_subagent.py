"""
Task Statement 1.3 — Web Search Subagent

Isolation principle in action: this function receives ONLY what is explicitly
passed in via `task_prompt`. It has no access to the coordinator's conversation
history, no memory of prior invocations. Everything it needs is in the prompt
the coordinator constructs for it.

Uses Claude's built-in server-side web_search tool (executed by Anthropic's
infrastructure, not our own tool_executor) — real search, not mocked.

Output contract: structured findings separating content from source metadata,
so attribution survives the handoff to the synthesis step (Task 1.3 fix for
the "claims with no citations" failure mode).
"""

import json
import anthropic
import os

# Read company Bifrost configuration from environment
api_key = os.getenv("BIFROST_API_KEY")
base_url = os.getenv("BIFROST_BASE_URL")

client = anthropic.Anthropic(   
        api_key=api_key,
        base_url=base_url)
MODEL = "anthropic/claude-sonnet-5"

SUBAGENT_SYSTEM_PROMPT = """You are a web research subagent. You have no memory \
of any other conversation — you only know what is in this prompt.

Research the assigned topic using web search. Specify goals and quality \
criteria, not procedure: find at least 3 credible, distinct sources.

When finished, output ONLY a JSON array (no prose, no markdown fences) of \
findings in this exact structure:
[
  {"content": "<the finding, 1-3 sentences>", "source_url": "<url>", "source_title": "<page title>"}
]
"""


def run_web_search_subagent(topic: str) -> list[dict]:
    """
    topic: the specific subtopic this subagent is responsible for researching.
    Returns: list of structured findings with content + source metadata.
    """
    task_prompt = (
        f"Research subtopic: {topic}\n\n"
        "Find at least 3 credible, distinct sources covering this specific "
        "subtopic. Do not drift into adjacent subtopics."
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=SUBAGENT_SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}],
        messages=[{"role": "user", "content": task_prompt}],
    )

    final_text = "".join(block.text for block in response.content if block.type == "text")

    try:
        findings = json.loads(_strip_fences(final_text))
    except json.JSONDecodeError:
        # Degrade gracefully rather than crashing the whole pipeline on a
        # formatting slip — the coordinator still gets something attributable.
        findings = [{"content": final_text.strip(), "source_url": None, "source_title": None}]

    return findings


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
    return text.strip()
