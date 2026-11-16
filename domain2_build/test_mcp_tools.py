"""
Part 1: Connect to the MCP server over stdio (simulating what .mcp.json
wires up) and directly exercise all three tools, proving all four error
categories plus the credential-loaded-from-env check.
"""

import asyncio
import json
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    # Mirrors what Claude Code does when it reads .mcp.json: it expands
    # ${CUSTOMER_API_TOKEN} from this process's environment before launching
    # the server subprocess.
    env = os.environ.copy()
    env.setdefault("CUSTOMER_API_TOKEN", "valid-token")

    server_params = StdioServerParameters(
        command="python3",
        args=["server.py"],
        env=env,
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("=== Tools discovered at connection time ===")
            for t in tools.tools:
                print(f"- {t.name}: {t.description[:70]}...")
            print()

            print("=== Credential loaded from env via .mcp.json expansion ===")
            r = await session.call_tool("check_server_credential_loaded", {})
            print(json.loads(r.content[0].text), "\n")

            print("=== VALIDATION error (malformed order ID) ===")
            r = await session.call_tool("process_refund", {
                "order_id": "BAD-ID", "amount": 50, "auth_token": "valid-token"
            })
            print(json.loads(r.content[0].text), "\n")

            print("=== PERMISSION error (bad auth token) ===")
            r = await session.call_tool("process_refund", {
                "order_id": "ORD-9001", "amount": 50, "auth_token": "wrong-token"
            })
            print(json.loads(r.content[0].text), "\n")

            print("=== TRANSIENT error (simulated gateway timeout) ===")
            r = await session.call_tool("process_refund", {
                "order_id": "ORD-TIMEOUT", "amount": 50, "auth_token": "valid-token"
            })
            print(json.loads(r.content[0].text), "\n")

            print("=== BUSINESS error (exceeds $500 limit, not retryable) ===")
            r = await session.call_tool("process_refund", {
                "order_id": "ORD-9002", "amount": 750, "auth_token": "valid-token"
            })
            print(json.loads(r.content[0].text), "\n")

            print("=== SUCCESS case ===")
            r = await session.call_tool("process_refund", {
                "order_id": "ORD-9003", "amount": 120, "auth_token": "valid-token"
            })
            print(json.loads(r.content[0].text), "\n")

            print("=== Valid empty result vs error (2.2 critical distinction) ===")
            r = await session.call_tool("get_customer_profile", {"customer_id": "C-UNKNOWN"})
            print("get_customer_profile(unknown customer):", json.loads(r.content[0].text))
            print("  -> isError: False, result: null. This is a SUCCESSFUL query")
            print("     that found nothing — NOT an access failure. Do not retry.\n")


if __name__ == "__main__":
    asyncio.run(main())
