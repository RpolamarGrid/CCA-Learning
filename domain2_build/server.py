"""
Task Statement 2.1 / 2.2 — MCP Server with 3 tools

Tools:
  1. get_customer_profile  -\
  2. get_customer_orders    >- intentionally ambiguous pair (see descriptions)
  3. process_refund        -- demonstrates all four error categories

The ambiguous pair is deliberate: both descriptions below are written in the
THIN style the exam calls out ("Retrieves [entity] information") so that a
query like "what did customer C-882 order recently?" can plausibly be routed
to either tool. Compare these against the FIXED versions in
server_fixed_descriptions.py to see the 2.1 remedy in action.
"""

import os
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("domain2-demo-server")

# Task 2.4: credential comes from the environment via .mcp.json's
# ${CUSTOMER_API_TOKEN} expansion — never hardcoded, never committed.
SERVER_API_TOKEN = os.environ.get("CUSTOMER_API_TOKEN", "")

# --- Fake in-memory data -----------------------------------------------

CUSTOMERS = {
    "C-882": {"name": "Priya Raman", "email": "priya@example.com", "tier": "gold"},
}

ORDERS = {
    "C-882": [
        {"order_id": "ORD-4471", "item": "Wireless Mouse", "status": "delivered"},
        {"order_id": "ORD-4502", "item": "USB-C Hub", "status": "in_transit"},
    ]
}

REFUND_LIMIT_NO_APPROVAL = 500


# --- Error response helper (Task 2.2: structured error metadata) --------

def error_response(category: str, message: str, retryable: bool) -> dict:
    """
    Builds a structured MCP-style error payload.
    category: "transient" | "validation" | "business" | "permission"
    """
    return {
        "isError": True,
        "errorCategory": category,
        "isRetryable": retryable,
        "description": message,
    }


def success_response(result) -> dict:
    """Explicit isError: False — distinguishes a genuine successful (possibly
    empty) result from a structured error. This is the fix for the
    access-failure-vs-valid-empty-result confusion taught in 2.2."""
    return {"isError": False, "result": result}


# --- AMBIGUOUS PAIR (intentionally thin descriptions) --------------------

@mcp.tool(description="Retrieves customer information.")
def get_customer_profile(customer_id: str) -> dict:
    """Thin description on purpose — this is tool #1 of the ambiguous pair."""
    customer = CUSTOMERS.get(customer_id)
    if customer is None:
        return success_response(None)  # valid empty result, NOT an error
    return success_response(customer)


@mcp.tool(description="Retrieves order information.")
def get_customer_orders(customer_id: str) -> dict:
    """Thin description on purpose — this is tool #2 of the ambiguous pair."""
    orders = ORDERS.get(customer_id, [])
    return success_response(orders)  # empty list is a VALID result, not an error


# --- process_refund: demonstrates all four error categories -------------

@mcp.tool(
    description=(
        "Processes a refund for a given order. Validates input, checks "
        "authorization, enforces the $500 manager-approval policy limit, "
        "and simulates downstream service calls. Returns a structured "
        "error with errorCategory (transient|validation|business|permission) "
        "and isRetryable when it cannot complete the refund."
    )
)
def process_refund(order_id: str, amount: float, auth_token: str) -> dict:
    # --- VALIDATION error: malformed/missing input ---
    if not order_id or not order_id.startswith("ORD-"):
        return error_response(
            "validation",
            f"'{order_id}' is not a valid order ID (expected format ORD-####).",
            retryable=True,  # retryable once the caller fixes the input
        )
    if amount <= 0:
        return error_response(
            "validation",
            "Refund amount must be a positive number.",
            retryable=True,
        )

    # --- PERMISSION error: missing/invalid auth ---
    if auth_token != "valid-token":
        return error_response(
            "permission",
            "Auth token is invalid or missing required refund-processing scope.",
            retryable=False,  # retrying the same call won't fix a bad token
        )

    # --- TRANSIENT error: simulated downstream flakiness ---
    # Deterministic trigger (rather than real randomness) so the demo script
    # can reliably exercise this path on request.
    if order_id == "ORD-TIMEOUT":
        return error_response(
            "transient",
            "Payment gateway timed out while processing the refund.",
            retryable=True,
        )

    # --- BUSINESS error: policy violation, not retryable ---
    if amount >= REFUND_LIMIT_NO_APPROVAL:
        return error_response(
            "business",
            f"Refund of ${amount:.2f} exceeds the ${REFUND_LIMIT_NO_APPROVAL} "
            "limit that can be processed without manager sign-off. "
            "Escalate for manager approval instead of retrying.",
            retryable=False,
        )

    # --- Success ---
    return success_response({
        "order_id": order_id,
        "refunded_amount": amount,
        "status": "refund_processed",
    })


@mcp.tool(
    description=(
        "Diagnostic tool: confirms whether the server loaded its API "
        "credential from the environment (via .mcp.json's ${CUSTOMER_API_TOKEN} "
        "expansion) without ever revealing the actual secret value."
    )
)
def check_server_credential_loaded() -> dict:
    loaded = bool(SERVER_API_TOKEN)
    masked = f"{SERVER_API_TOKEN[:2]}***{SERVER_API_TOKEN[-2:]}" if loaded and len(SERVER_API_TOKEN) > 4 else None
    return success_response({"credential_loaded": loaded, "masked_preview": masked})


if __name__ == "__main__":
    mcp.run(transport="stdio")
