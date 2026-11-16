"""
Task Statements 1.2 / 1.3 / 1.4 — Coordinator

Hub-and-spoke: this coordinator is the only thing that talks to the two
subagents. The subagents never talk to each other. All aggregation, error
handling, and the prerequisite gate live here.

Decomposition strategy: dynamic adaptive (Task 1.6) — the coordinator reads
the multi-concern request and decides, at runtime, which subtopics/focus
areas to assign. It does not run a fixed hardcoded pipeline, because an
open-ended multi-concern request like this one is exactly the "don't know
the shape in advance" case from 1.6.

Isolation principle (1.2) in action: notice that `web_topic` and
`doc_focus` are the ONLY things handed to each subagent. Neither subagent
sees this coordinator's own reasoning, the other subagent's output, or
the original user request verbatim — only what's explicitly written into
its task prompt.
"""

import json
import anthropic
import os
from web_search_subagent import run_web_search_subagent
from document_subagent import run_document_subagent
from hooks import normalize_subagent_output, prerequisite_gate, PrerequisiteNotMetError

# Read company Bifrost configuration from environment
api_key = os.getenv("BIFROST_API_KEY")
base_url = os.getenv("BIFROST_BASE_URL")

client = anthropic.Anthropic(   
        api_key=api_key,
        base_url=base_url)
MODEL = "anthropic/claude-sonnet-5"

DECOMPOSE_SYSTEM_PROMPT = """You are a coordinator agent decomposing a \
multi-concern user request into subagent assignments.

You have exactly two subagent types available:
- web_search: researches a topic on the open web
- document_analysis: extracts findings from a local policy document

Given the user's request, decide:
1. A concise topic string for the web_search subagent
2. A concise focus_area string for the document_analysis subagent

Respond with ONLY JSON, no prose, no markdown fences:
{"web_topic": "...", "doc_focus": "..."}
"""

SYNTHESIS_SYSTEM_PROMPT = """You are a coordinator synthesising findings from \
two independent subagents into one unified answer addressing the user's \
original multi-concern request.

Every claim you make MUST be traceable to a provided finding. Cite the \
source_label and source_location inline for each claim, e.g. (Acme Refund \
Policy, page 2) or (TechCrunch, https://...).

Address each concern in the original request explicitly — do not drop any \
of them.
"""


def decompose_request(user_request: str) -> dict:
    """Dynamic adaptive decomposition (Task 1.6): the split is decided at
    runtime based on the actual request, not a fixed predetermined pipeline.
    """
    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        system=DECOMPOSE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_request}],
    )
    text = "".join(b.text for b in response.content if b.type == "text")
    return json.loads(_strip_fences(text))


def run_coordinator(user_request: str, document_path: str) -> str:
    print(f"\n=== COORDINATOR: received multi-concern request ===\n{user_request}\n")

    # --- Task decomposition (1.6, dynamic adaptive) ---
    plan = decompose_request(user_request)
    print(f"[coordinator] decomposition plan: {plan}\n")

    completed_subagents = set()
    required_subagents = {"web_search", "document_analysis"}
    normalized_findings = []

    # --- Parallel-intent spawning (1.3) ---
    # (Executed sequentially here since this is a plain script, not the Task
    # tool's native parallel dispatch — but each call is independent and
    # isolated, which is the property that actually matters for 1.2/1.3.)

    print(f"[coordinator] -> invoking web_search subagent on: {plan['web_topic']!r}")
    print("  (isolation check: this subagent sees ONLY the topic string above —")
    print("   not this coordinator's reasoning, not the user's raw request)")
    web_raw = run_web_search_subagent(topic=plan["web_topic"])
    web_normalized = normalize_subagent_output("web_search", web_raw)  # PostToolUse hook (1.5)
    normalized_findings.extend(web_normalized)
    completed_subagents.add("web_search")
    print(f"  <- web_search returned {len(web_normalized)} normalized findings\n")

    print(f"[coordinator] -> invoking document_analysis subagent, focus: {plan['doc_focus']!r}")
    print("  (isolation check: this subagent sees ONLY the file path + focus area —")
    print("   not the web_search subagent's findings)")
    doc_raw = run_document_subagent(file_path=document_path, focus_area=plan["doc_focus"])
    doc_normalized = normalize_subagent_output("document_analysis", doc_raw)  # PostToolUse hook (1.5)
    normalized_findings.extend(doc_normalized)
    completed_subagents.add("document_analysis")
    print(f"  <- document_analysis returned {len(doc_normalized)} normalized findings\n")

    # --- Programmatic prerequisite gate (1.4 / 1.5) ---
    # This call MUST succeed because both subagents completed above. The
    # second demo run (see main.py) proves it blocks when they haven't.
    prerequisite_gate("finalize_report", completed_subagents, required_subagents)
    print("[coordinator] prerequisite gate PASSED — both subagents completed, "
          "finalize_report is permitted to run\n")

    # --- Synthesis (context passing with structured metadata, 1.3) ---
    synthesis_input = json.dumps(normalized_findings, indent=2)
    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        system=SYNTHESIS_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": (
                f"Original user request:\n{user_request}\n\n"
                f"Normalized findings from both subagents (full structured "
                f"data, not summarised — nothing was dropped):\n{synthesis_input}"
            ),
        }],
    )
    final_report = "".join(b.text for b in response.content if b.type == "text")
    return final_report


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
    return text.strip()
