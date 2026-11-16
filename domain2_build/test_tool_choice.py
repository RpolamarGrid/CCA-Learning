"""
Part 3: Task 2.3 — tool_choice modes.

Demonstrates the three modes against the same request, side by side:
  - "auto": model decides whether/which tool to call
  - "any": model MUST call some tool, but picks which one
  - {"type": "tool", "name": "..."}: model MUST call that EXACT tool

Scenario: a workflow requires `extract_metadata` to run as a mandatory first
step before any enrichment tool is considered. We show that only the named
forced-tool mode actually guarantees this.
"""

import anthropic
import os

# Read company Bifrost configuration from environment
api_key = os.getenv("BIFROST_API_KEY")
base_url = os.getenv("BIFROST_BASE_URL")

client = anthropic.Anthropic(api_key=api_key, base_url=base_url)
MODEL = "anthropic/claude-sonnet-5"

TOOLS = [
    {
        "name": "extract_metadata",
        "description": "Extracts structured metadata (title, author, date) from raw input text.",
        "input_schema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
    {
        "name": "summarize_content",
        "description": "Produces a short summary of the given text.",
        "input_schema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
]

# A request that doesn't obviously ask for metadata extraction at all —
# under "auto", the model may reasonably skip straight to summarising.
REQUEST = "Here's a document: 'The Rise of Renewable Energy, by J. Alder, 2026-01-10. ...'. Can you tell me what this is about?"


def show(label, tool_choice):
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        tools=TOOLS,
        tool_choice=tool_choice,
        messages=[{"role": "user", "content": REQUEST}],
    )
    called = [b.name for b in response.content if b.type == "tool_use"]
    print(f"[{label}] tool_choice={tool_choice}")
    print(f"[{label}] stop_reason={response.stop_reason}")
    print(f"[{label}] tool(s) called={called}\n")
    return called


if __name__ == "__main__":
    print("=== auto: model decides freely whether/which tool to call ===")
    auto_called = show("auto", {"type": "auto"})

    print("=== any: model MUST call a tool, but chooses which ===")
    any_called = show("any", {"type": "any"})

    print("=== forced named tool: model MUST call extract_metadata specifically ===")
    forced_called = show("forced", {"type": "tool", "name": "extract_metadata"})

    # Build the takeaway from what THIS run actually produced, not a
    # hardcoded narration of some earlier run's output.
    lines = ["Takeaway (from the actual run above):"]

    if "extract_metadata" not in auto_called:
        lines.append(
            "- 'auto' did not call extract_metadata at all this run "
            f"(called {auto_called or 'nothing'}) — the model judged it "
            "unnecessary and skipped the mandatory step entirely."
        )
    else:
        lines.append(
            f"- 'auto' happened to include extract_metadata this run "
            f"(called {auto_called}), but 'auto' never GUARANTEES this — "
            "it's free to omit it on a different request or phrasing."
        )

    if "extract_metadata" not in any_called:
        lines.append(
            f"- 'any' guaranteed SOME tool call but picked {any_called}, "
            "skipping extract_metadata — proving 'any' cannot enforce "
            "WHICH tool runs, only THAT one runs."
        )
    else:
        lines.append(
            f"- 'any' happened to include extract_metadata this run "
            f"(called {any_called}), but this is NOT guaranteed by 'any' — "
            "it only guarantees some tool is called, not a specific one."
        )

    if forced_called and forced_called[0] == "extract_metadata":
        lines.append(
            "- The named-tool force correctly guaranteed extract_metadata "
            f"ran first this run (called {forced_called}) — this is the "
            "only mode of the three that deterministically enforces it."
        )
    else:
        lines.append(
            f"- UNEXPECTED: forced tool_choice did not produce "
            f"extract_metadata first (called {forced_called}) — investigate."
        )

    print("\n".join(lines))
