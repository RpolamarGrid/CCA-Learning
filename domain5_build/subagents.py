"""
Task 5.3 — structured error propagation (simulated timeout).
Task 5.6 — structured claim-source mappings, conflicting sources preserved.

Subagent 1: order_lookup_subagent -- simulates a tool timeout to exercise
structured error propagation (NOT silent suppression, NOT workflow
termination).

Subagent 2: refund_policy_research_subagent -- returns genuinely
conflicting information about standard refund processing time, each
tagged with full source metadata (claim, source_label, publication_date),
to test whether synthesis preserves the conflict rather than picking one.
"""

import os
import anthropic
from case_facts import CaseFacts

client = anthropic.Anthropic(
    api_key=os.getenv("BIFROST_API_KEY"),
    base_url=os.getenv("BIFROST_BASE_URL"),
)
MODEL = "anthropic/claude-sonnet-5"


class TimeoutError_(Exception):
    """Simulated transient tool failure."""


def order_lookup_subagent(case_facts: CaseFacts, simulate_timeout: bool) -> dict:
    """
    Isolated subagent (Domain 1 isolation principle): receives ONLY the
    case facts block it needs, not the full coordinator conversation.

    Returns a structured result dict. On simulated timeout, returns
    STRUCTURED ERROR CONTEXT per Task 5.3 -- failure type, what was
    attempted, partial results gathered before failure, and potential
    alternative approaches. This is deliberately NOT silent suppression
    (empty-marked-success) and NOT a thrown exception that would kill
    the whole pipeline.
    """
    attempted_query = f"GET /orders/{case_facts.order_id}/status"

    if simulate_timeout:
        return {
            "subagent": "order_lookup",
            "isError": True,
            "errorCategory": "transient",
            "isRetryable": True,
            "what_was_attempted": attempted_query,
            "partial_results": {
                "order_id_confirmed_valid_format": True,
                "status_field": None,  # never reached before timeout
            },
            "alternative_approaches": [
                "Retry with backoff (transient failure, likely to succeed)",
                "Fall back to cached order status from last successful sync, "
                "if available, with a staleness warning",
            ],
            "description": (
                f"Order status lookup for {case_facts.order_id} timed out "
                "after 30s waiting on the fulfillment service."
            ),
        }

    # Non-timeout path: successful lookup
    return {
        "subagent": "order_lookup",
        "isError": False,
        "result": {"order_id": case_facts.order_id, "status": "delivered",
                    "delivered_date": "2026-10-20"},
    }


def refund_policy_research_subagent() -> dict:
    """
    Isolated subagent researching "standard refund processing time" for
    context on the customer's case. Deliberately returns two genuinely
    conflicting claims, each with full source metadata, to test whether
    the coordinator's synthesis step preserves BOTH rather than picking
    one arbitrarily (Task 5.6).
    """
    findings = [
        {
            "claim": "Standard refund processing time is 5-7 business days.",
            "source_label": "Company Refund Policy v3 (internal doc)",
            "publication_date": "2025-01-15",
            "excerpt": "Refunds are processed within 5-7 business days of approval.",
        },
        {
            "claim": "Standard refund processing time is 3-5 business days.",
            "source_label": "Company Refund Policy v4 (internal doc, updated)",
            "publication_date": "2026-06-01",
            "excerpt": "Effective June 2026, refunds are processed within 3-5 business days.",
        },
    ]
    return {"subagent": "refund_policy_research", "isError": False, "findings": findings}
