"""
End-to-end test, Task 1.4's multi-concern request pattern:
decompose into distinct concerns -> investigate each -> synthesise one
unified answer.

Also proves the prerequisite gate (1.4/1.5) actually blocks finalize_report
when a required subagent hasn't completed — not just that it passes when
everything is fine.
"""

from pathlib import Path

from coordinator import run_coordinator
from hooks import prerequisite_gate, PrerequisiteNotMetError

DOCUMENT_PATH = str(Path(__file__).parent / "sample_policy.txt")

MULTI_CONCERN_REQUEST = (
    "Two things: (1) what are current industry best practices for refund "
    "fraud prevention in customer support, based on recent sources, and "
    "(2) according to our internal policy document, what specifically "
    "requires manager sign-off, and what must a human escalation handoff "
    "contain?"
)


def demo_gate_blocks_when_subagent_skipped():
    print("=== DEMO: prerequisite gate blocks an incomplete pipeline ===")
    completed = {"web_search"}  # document_analysis deliberately NOT run
    required = {"web_search", "document_analysis"}
    try:
        prerequisite_gate("finalize_report", completed, required)
        print("UNEXPECTED: gate did not block — this would be a bug.\n")
    except PrerequisiteNotMetError as e:
        print(f"EXPECTED: gate correctly blocked -> {e}\n")


if __name__ == "__main__":
    demo_gate_blocks_when_subagent_skipped()

    report = run_coordinator(MULTI_CONCERN_REQUEST, DOCUMENT_PATH)

    print("=== FINAL SYNTHESISED REPORT ===\n")
    print(report)
