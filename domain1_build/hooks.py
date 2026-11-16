"""
Task Statement 1.5 — Hooks

Two distinct hook types, kept deliberately separate so the difference is
unmistakable:

1. PostToolUse hook (normalize_subagent_output):
   Runs AFTER a subagent "tool" (from the coordinator's point of view, each
   subagent invocation IS a tool call) returns, BEFORE the coordinator
   reasons about it. Normalises heterogeneous shapes (web search uses
   source_url/source_title, document analysis uses document_name/page_number)
   into ONE consistent schema. This is about data quality/consistency —
   nothing is blocked here, the subagent already ran.

2. Pre-execution interception hook (prerequisite_gate):
   Runs BEFORE a tool is allowed to execute. Physically blocks the
   finalize_report tool from firing unless both subagents have already
   returned results. This is deterministic enforcement, not a prompt asking
   the coordinator nicely to "wait for both subagents" — the gate raises if
   the precondition isn't met, full stop.
"""


def normalize_subagent_output(source_type: str, raw_findings: list[dict]) -> list[dict]:
    """
    PostToolUse hook. Maps web_search / document_analysis output shapes into
    one unified schema:
        {content, source_type, source_label, source_location}

    source_label / source_location let us trace a claim back to either a URL
    or a (document, page) pair without the synthesis step needing to know
    which subagent produced it.
    """
    normalized = []
    for finding in raw_findings:
        if source_type == "web_search":
            normalized.append({
                "content": finding.get("content", ""),
                "source_type": "web",
                "source_label": finding.get("source_title") or "Untitled source",
                "source_location": finding.get("source_url"),
            })
        elif source_type == "document_analysis":
            page = finding.get("page_number")
            normalized.append({
                "content": finding.get("content", ""),
                "source_type": "document",
                "source_label": finding.get("document_name", "unknown document"),
                "source_location": f"page {page}" if page is not None else "page unknown",
            })
        else:
            raise ValueError(f"Unknown source_type for normalisation: {source_type}")
    return normalized


class PrerequisiteNotMetError(RuntimeError):
    """Raised when a gated tool is called before its prerequisites are satisfied."""


def prerequisite_gate(tool_name: str, completed_subagents: set[str], required: set[str]) -> None:
    """
    Pre-execution tool call interception hook.

    Blocks `finalize_report` (the high-stakes action here, analogous to a
    refund tool in the support-agent scenario) until every subagent in
    `required` has completed. This mirrors Task 1.4's rule: when consequences
    matter (here: shipping an incomplete/unattributed report), enforcement
    must be programmatic, not "the coordinator's prompt told it to wait."
    """
    if tool_name != "finalize_report":
        return  # gate only applies to the high-stakes action

    missing = required - completed_subagents
    if missing:
        raise PrerequisiteNotMetError(
            f"BLOCKED: finalize_report cannot run — missing results from: {sorted(missing)}. "
            "This is enforced in code, not by asking the coordinator nicely."
        )
