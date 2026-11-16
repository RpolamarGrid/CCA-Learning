"""
Task Statement 1.1 — Agentic Loop

The ONLY correct way to detect loop completion: check `stop_reason`.
- stop_reason == "tool_use"  -> execute tools, append results, send back
- stop_reason == "end_turn"  -> done, return final response

Anti-patterns deliberately NOT used here:
- Parsing assistant text for phrases like "I'm done"
- Using an iteration cap as the PRIMARY stop signal (we use one only as a safety ceiling)
- Treating "response contains text" as completion (text can accompany tool_use)
"""

import anthropic
import os

# Read company Bifrost configuration from environment
api_key = os.getenv("BIFROST_API_KEY")
base_url = os.getenv("BIFROST_BASE_URL")

client = anthropic.Anthropic(   
        api_key=api_key,
        base_url=base_url)
MODEL = "anthropic/claude-sonnet-5"
SAFETY_MAX_ITERATIONS = 15  # backstop only, never the primary termination signal


def run_agentic_loop(system_prompt, messages, tools, tool_executor, label="agent"):
    """
    Runs the full agentic loop for a single agent (coordinator or subagent).

    messages: list of message dicts, mutated/extended in place and returned
    tools: list of tool schemas available to this agent
    tool_executor: callable(tool_name: str, tool_input: dict) -> str
                   executes a single tool call and returns a string result

    Returns: (final_text, messages) where final_text is the agent's final
             end_turn response text.
    """
    for iteration in range(1, SAFETY_MAX_ITERATIONS + 1):
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=system_prompt,
            messages=messages,
            tools=tools,
        )

        # Append assistant turn (may contain text AND tool_use blocks together —
        # this is exactly why we never check "is there text?" to decide completion)
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"  [{label}] -> tool_use: {block.name}({block.input})")
                    result_text = tool_executor(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_text,
                    })
            # Tool results appended as a new user message so the model can
            # reason about the new information on the next iteration.
            messages.append({"role": "user", "content": tool_results})
            continue  # loop again — model has not signalled completion

        if response.stop_reason == "end_turn":
            final_text = "".join(
                block.text for block in response.content if block.type == "text"
            )
            return final_text, messages

        # Any other stop_reason (max_tokens, stop_sequence, etc.) — surface it
        # rather than silently treating it as success.
        raise RuntimeError(f"[{label}] Unexpected stop_reason: {response.stop_reason}")

    raise RuntimeError(
        f"[{label}] Hit safety iteration cap ({SAFETY_MAX_ITERATIONS}) without end_turn. "
        "This is a backstop, not expected behaviour — investigate the loop."
    )
