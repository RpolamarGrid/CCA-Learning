"""
Part 2: Task 2.1 — prove the ambiguous pair causes misrouting, and that
expanding descriptions (not few-shot, not a classifier, not consolidation)
fixes it.

We don't need a live MCP connection for this — tool_choice/selection is a
property of the Messages API given a tool schema, so we hand-build the two
schema variants (thin vs expanded) and send the identical ambiguous query
to each.
"""

import anthropic
import os

# Read company Bifrost configuration from environment
api_key = os.getenv("BIFROST_API_KEY")
base_url = os.getenv("BIFROST_BASE_URL")

client = anthropic.Anthropic(api_key=api_key, base_url=base_url)  # no live connection needed
MODEL = "anthropic/claude-sonnet-5"

AMBIGUOUS_QUERY = "Look up account C-882 and tell me what's going on with it."

# --- Variant A: thin, ambiguous descriptions (matches server.py) --------

THIN_TOOLS = [
    {
        "name": "get_customer_profile",
        "description": "Retrieves customer information.",
        "input_schema": {
            "type": "object",
            "properties": {"customer_id": {"type": "string"}},
            "required": ["customer_id"],
        },
    },
    {
        "name": "get_customer_orders",
        "description": "Retrieves order information.",
        "input_schema": {
            "type": "object",
            "properties": {"customer_id": {"type": "string"}},
            "required": ["customer_id"],
        },
    },
]

# --- Variant B: expanded, boundary-explicit descriptions (2.1 fix) ------

FIXED_TOOLS = [
    {
        "name": "get_customer_profile",
        "description": (
            "Retrieves a customer's PROFILE information: name, email, "
            "account tier. Use this for questions about WHO the customer "
            "is. Example queries: 'what's the email on file for C-882?', "
            "'what tier is this customer?'. Do NOT use this for questions "
            "about orders, shipments, or purchase history — use "
            "get_customer_orders for anything order-related."
        ),
        "input_schema": THIN_TOOLS[0]["input_schema"],
    },
    {
        "name": "get_customer_orders",
        "description": (
            "Retrieves a customer's ORDER information: order IDs, items "
            "purchased, shipment status. Use this for questions about WHAT "
            "a customer bought or ordered, and its delivery status. "
            "Example queries: 'what did customer C-882 order recently?', "
            "'is order ORD-4502 delivered yet?'. Do NOT use this for "
            "questions about the customer's identity, email, or account "
            "tier — use get_customer_profile for that."
        ),
        "input_schema": THIN_TOOLS[1]["input_schema"],
    },
]


def which_tool_called(tools_schema):
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        tools=tools_schema,
        tool_choice={"type": "auto"},
        messages=[{"role": "user", "content": AMBIGUOUS_QUERY}],
    )
    called = [b.name for b in response.content if b.type == "tool_use"]
    return called[0] if called else None


def run_trials(tools_schema, label, n=5):
    results = [which_tool_called(tools_schema) for _ in range(n)]
    print(f"[{label}] query: {AMBIGUOUS_QUERY!r}")
    print(f"[{label}] tool picked across {n} runs: {results}")
    distinct = set(results)
    if len(distinct) > 1:
        print(f"[{label}] INCONSISTENT routing — same query picked different "
              f"tools across runs ({distinct}). This is the misrouting problem.\n")
    else:
        print(f"[{label}] CONSISTENT routing — every run picked {distinct}.\n")


if __name__ == "__main__":
    print("=== Variant A: thin, ambiguous descriptions ===")
    run_trials(THIN_TOOLS, "thin")

    print("=== Variant B: expanded, boundary-explicit descriptions (2.1 fix) ===")
    run_trials(FIXED_TOOLS, "fixed")

    print(
        "NOTE: Claude Sonnet 5 is strong enough to route this correctly even\n"
        "with thin descriptions in this test — it infers intent from context.\n"
        "The exam's underlying principle still holds (description quality IS\n"
        "the mechanism tool selection relies on), but modern models are more\n"
        "resilient to thin descriptions than the exam's worst-case scenario\n"
        "assumes. The fix (expand descriptions with explicit boundaries) is\n"
        "still correct best practice — it removes reliance on the model's\n"
        "ability to infer intent, which matters more as tool count/overlap\n"
        "grows beyond this toy example's 2 tools."
    )
