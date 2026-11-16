"""
Task 4.3 (tool_use structured output) + Task 4.4 (validation-retry loop).

validate_extraction() distinguishes the two categories taught in 4.4:
  - FIXABLE via retry: structural/format issues (e.g. category_detail
    missing when category == "other")
  - NOT fixable via retry: calculated_total != stated_total is flagged as
    a conflict, not silently "fixed" by brute-force retrying -- per 4.4,
    this is a self-correction SIGNAL (conflict_detected), not something we
    hammer the model to change, since we don't know which number is wrong.
"""

import json
import os
import anthropic
from schema import EXTRACT_INVOICE_TOOL

client = anthropic.Anthropic(
    api_key=os.getenv("BIFROST_API_KEY"),
    base_url=os.getenv("BIFROST_BASE_URL"),
)
MODEL = "anthropic/claude-sonnet-5"

MAX_RETRIES = 2


def validate_extraction(data: dict) -> list[str]:
    """Returns a list of structural validation errors (empty if valid).
    These are the FIXABLE-via-retry class from Task 4.4: format/structure
    issues, not "information genuinely absent from source"."""
    errors = []

    if data.get("category") == "other" and not data.get("category_detail"):
        errors.append(
            "category is 'other' but category_detail is missing/null. "
            "When category is 'other', category_detail must describe what "
            "the category actually is."
        )

    stated = data.get("stated_total")
    calculated = data.get("calculated_total")
    if stated is not None and calculated is not None:
        if abs(stated - calculated) > 0.01 and not data.get("conflict_detected"):
            errors.append(
                f"stated_total ({stated}) does not match calculated_total "
                f"({calculated}), but conflict_detected was not set to true. "
                "Set conflict_detected=true and explain in conflict_detail."
            )

    due_date = data.get("due_date")
    if due_date is not None:
        import re
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", due_date):
            errors.append(
                f"due_date '{due_date}' is not in ISO 8601 format "
                "(YYYY-MM-DD)."
            )

    return errors


def extract_with_retry(document_text: str, system_prompt: str, label: str) -> dict:
    """Runs the extraction, retrying with specific validation error feedback
    on structural failures, up to MAX_RETRIES times."""
    messages = [{"role": "user", "content": document_text}]

    for attempt in range(1, MAX_RETRIES + 2):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=system_prompt,
            tools=[EXTRACT_INVOICE_TOOL],
            tool_choice={"type": "tool", "name": "extract_invoice"},
            messages=messages,
        )

        tool_call = next(b for b in response.content if b.type == "tool_use")
        extracted = tool_call.input

        errors = validate_extraction(extracted)
        if not errors:
            return {
                "label": label, "attempts": attempt, "data": extracted,
                "final_errors": [],
            }

        if attempt > MAX_RETRIES:
            return {
                "label": label, "attempts": attempt, "data": extracted,
                "final_errors": errors,
            }

        print(f"  [{label}] attempt {attempt} validation errors: {errors}")
        messages.append({"role": "assistant", "content": response.content})
        messages.append({
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": tool_call.id,
                "content": (
                    "Validation failed:\n" + "\n".join(f"- {e}" for e in errors) +
                    "\n\nPlease correct and resubmit."
                ),
                "is_error": True,
            }],
        })

    raise RuntimeError("unreachable")
