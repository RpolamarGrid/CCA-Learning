from case_facts import CaseFacts
from coordinator import run_support_case

case = CaseFacts(
    customer_name="Jordan Ellis",
    order_id="ORD-55210",
    refund_amount=247.83,
    order_date="2026-03-03",
    complaint="Item arrived damaged and I want a refund, not a replacement.",
)

if __name__ == "__main__":
    print("##### RUN: order_lookup TIMES OUT #####")
    output = run_support_case(case, simulate_timeout=True)
    print("\n=== FINAL SYNTHESIS OUTPUT ===\n")
    print(output)

    print("\n\n" + "=" * 70)
    print("VERIFICATION CHECKS")
    print("=" * 70)

    checks = {
        "exact refund amount ($247.83) preserved verbatim": "247.83" in output,
        "exact order ID (ORD-55210) preserved verbatim": "ORD-55210" in output,
        "timeout error mentioned, not silently ignored": (
            "timeout" in output.lower() or "timed out" in output.lower()
        ),
        "both conflicting refund-time values present (5-7 AND 3-5)": (
            ("5-7" in output or "5–7" in output) and
            ("3-5" in output or "3–5" in output)
        ),
    }
    for label, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {label}")
