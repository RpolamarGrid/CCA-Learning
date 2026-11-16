"""
Runs all 10 documents through extraction TWICE:
  1. BASELINE: system prompt only, no few-shot examples
  2. FEW-SHOT: same system prompt + 3 reasoning-annotated examples covering
     varied formats (narrative, table, missing-field, ambiguous-category)

Then prints an honest before/after comparison -- including any cases where
few-shot does NOT visibly help, since Sonnet 5 is already strong (as we saw
in Domain 2's routing test) and overclaiming improvement would be dishonest.
"""

import json
from pathlib import Path

from extractor import extract_with_retry

DOCS_DIR = Path(__file__).parent / "documents"

BASELINE_SYSTEM_PROMPT = """You are an invoice extraction assistant. Extract \
structured data using the extract_invoice tool. Leave fields null when the \
source document does not state that information -- never invent values. \
Compute calculated_total yourself from the line items; do not copy it from \
stated_total."""

FEW_SHOT_SYSTEM_PROMPT = BASELINE_SYSTEM_PROMPT + """

Here are examples of handling varied document formats correctly:

Example 1 (narrative style, no explicit "Tax ID:" label):
Document: "...Our tax identification number is LLP-TAX-7781..."
Reasoning: the phrase "tax identification number" is semantically the same
as "Tax ID" even though it's phrased narratively rather than labelled --
extract LLP-TAX-7781 rather than returning null just because the exact
label "Tax ID:" doesn't appear.

Example 2 (payment status truly unstated):
Document: lists line items and a total, but never mentions whether the
invoice was paid, unpaid, or partially paid anywhere in the text.
Reasoning: do NOT infer "unpaid" just because no payment confirmation
appears -- absence of a payment mention is not evidence of non-payment.
Use payment_status="unclear" instead of guessing.

Example 3 (category doesn't fit predefined list):
Document: an invoice for landscaping/garden maintenance services.
Reasoning: "landscaping" doesn't match software/consulting/hardware/travel.
Rather than forcing it into the closest-sounding wrong category, use
category="other" and set category_detail="landscaping and grounds
maintenance services" so the information isn't lost.
"""


def run_batch(system_prompt: str, run_label: str) -> list[dict]:
    results = []
    for doc_path in sorted(DOCS_DIR.glob("*.txt")):
        text = doc_path.read_text()
        result = extract_with_retry(text, system_prompt, label=doc_path.stem)
        results.append(result)
        print(f"[{run_label}] {doc_path.stem}: {result['attempts']} attempt(s), "
              f"errors={result['final_errors']}")
    return results


def summarize(results: list[dict], run_label: str):
    null_tax_id = sum(1 for r in results if r["data"].get("tax_id") is None)
    unclear_status = sum(1 for r in results if r["data"].get("payment_status") == "unclear")
    other_category = sum(1 for r in results if r["data"].get("category") == "other")
    conflicts = sum(1 for r in results if r["data"].get("conflict_detected"))
    retried = sum(1 for r in results if r["attempts"] > 1)
    unresolved = sum(1 for r in results if r["final_errors"])

    print(f"\n=== Summary: {run_label} ===")
    print(f"  tax_id correctly null: {null_tax_id}")
    print(f"  payment_status 'unclear' used: {unclear_status}")
    print(f"  category 'other' used: {other_category}")
    print(f"  conflict_detected=true: {conflicts}")
    print(f"  documents needing retry: {retried}/10")
    print(f"  documents with unresolved validation errors: {unresolved}/10")


if __name__ == "__main__":
    print("########## RUN 1: BASELINE (no few-shot) ##########")
    baseline_results = run_batch(BASELINE_SYSTEM_PROMPT, "baseline")
    summarize(baseline_results, "BASELINE")

    print("\n########## RUN 2: FEW-SHOT (3 reasoning-annotated examples) ##########")
    fewshot_results = run_batch(FEW_SHOT_SYSTEM_PROMPT, "few-shot")
    summarize(fewshot_results, "FEW-SHOT")

    Path("baseline_results.json").write_text(
        json.dumps(baseline_results, indent=2, default=str)
    )
    Path("fewshot_results.json").write_text(
        json.dumps(fewshot_results, indent=2, default=str)
    )
    print("\nFull results written to baseline_results.json / fewshot_results.json")
