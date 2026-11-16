"""
Coordinator: injects the case facts block verbatim into subagent context
(Task 5.1), invokes both subagents, handles the timeout via structured
error propagation rather than silent suppression or workflow termination
(Task 5.3), and synthesises a final response that preserves BOTH source
attribution for conflicting claims (Task 5.6) and the exact case facts
(Task 5.1) without rounding or paraphrasing them.
"""

import json
import os
import anthropic

from case_facts import CaseFacts
from subagents import order_lookup_subagent, refund_policy_research_subagent

client = anthropic.Anthropic(
    api_key=os.getenv("BIFROST_API_KEY"),
    base_url=os.getenv("BIFROST_BASE_URL"),
)
MODEL = "anthropic/claude-sonnet-5"

SYNTHESIS_SYSTEM_PROMPT = """You are a customer support coordinator \
synthesising subagent results into a response plan.

CRITICAL RULES:
1. The case facts block is VERBATIM data -- reproduce the exact amount, \
order ID, and date. Never round, paraphrase, or approximate them.
2. If a subagent result is a structured error (isError: true), do NOT \
pretend it succeeded and do NOT halt -- explain what happened, what was \
attempted, and what the next step should be, using the partial_results \
and alternative_approaches provided.
3. If research findings conflict (e.g. two different values for the same \
thing), you MUST present BOTH values with their source labels and \
publication dates. Do NOT arbitrarily pick one. If the dates differ, note \
that the more recent source may simply reflect an updated policy rather \
than a contradiction.
"""


def run_support_case(case_facts: CaseFacts, simulate_timeout: bool) -> str:
    print(f"\n=== CASE FACTS BLOCK (will be injected verbatim) ===")
    print(case_facts.as_block())

    print("=== Invoking order_lookup_subagent (isolated context) ===")
    order_result = order_lookup_subagent(case_facts, simulate_timeout=simulate_timeout)
    if order_result["isError"]:
        print(f"  -> STRUCTURED ERROR (not silently suppressed, not halting pipeline):")
        print(f"     errorCategory={order_result['errorCategory']}, "
              f"isRetryable={order_result['isRetryable']}")
    else:
        print(f"  -> success: {order_result['result']}")

    print("\n=== Invoking refund_policy_research_subagent (isolated context) ===")
    research_result = refund_policy_research_subagent()
    print(f"  -> {len(research_result['findings'])} findings returned, "
          f"with full source metadata")

    # Pipeline continues regardless of the order_lookup failure -- this IS
    # the "do not halt the whole pipeline on one failure" fix from 5.3.
    synthesis_input = {
        "case_facts": case_facts.as_dict(),
        "order_lookup_result": order_result,
        "refund_policy_findings": research_result["findings"],
    }

    print("\n=== Synthesising final response ===")
    response = client.messages.create(
        model=MODEL,
        max_tokens=1200,
        system=SYNTHESIS_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": (
                f"{case_facts.as_block()}\n"
                f"Subagent results (full structured data, including any "
                f"errors and any conflicting findings -- nothing has been "
                f"pre-resolved for you):\n{json.dumps(synthesis_input, indent=2)}\n\n"
                "Write the customer-facing response plan."
            ),
        }],
    )
    return "".join(b.text for b in response.content if b.type == "text")
