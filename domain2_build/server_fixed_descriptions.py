"""
Task 2.1 remedy, side-by-side comparison.

Same two tools as the ambiguous pair in server.py, but with the exam's
preferred fix applied: expanded descriptions with explicit boundary
language — NOT few-shot examples, NOT a routing classifier, NOT
consolidation. This file is not wired into .mcp.json; it exists purely so
test_routing.py can run the identical query against both versions and show
the difference a description rewrite makes.
"""

from mcp.server.mcpserver import MCPServer
from server import CUSTOMERS, ORDERS, success_response

mcp = MCPServer("domain2-demo-server-fixed")


@mcp.tool(
    description=(
        "Retrieves a customer's PROFILE information: name, email, account "
        "tier. Use this for questions about WHO the customer is. "
        "Example queries: 'what's the email on file for C-882?', "
        "'what tier is this customer?'. "
        "Do NOT use this for questions about orders, shipments, or purchase "
        "history — use get_customer_orders for anything order-related."
    )
)
def get_customer_profile(customer_id: str) -> dict:
    customer = CUSTOMERS.get(customer_id)
    return success_response(customer)


@mcp.tool(
    description=(
        "Retrieves a customer's ORDER information: order IDs, items "
        "purchased, shipment status. Use this for questions about WHAT a "
        "customer bought or ordered, and its delivery status. "
        "Example queries: 'what did customer C-882 order recently?', "
        "'is order ORD-4502 delivered yet?'. "
        "Do NOT use this for questions about the customer's identity, "
        "email, or account tier — use get_customer_profile for that."
    )
)
def get_customer_orders(customer_id: str) -> dict:
    orders = ORDERS.get(customer_id, [])
    return success_response(orders)


if __name__ == "__main__":
    mcp.run(transport="stdio")
