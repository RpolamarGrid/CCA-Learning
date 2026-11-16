"""
The 10-document run never triggered a real retry (Sonnet 5 didn't make
structural mistakes). To actually prove the validation-retry loop works --
not just that it's unused code -- this test forces a validation failure
directly against validate_extraction() and confirms detection logic fires
correctly for each of the three rules.
"""

from extractor import validate_extraction

# Case 1: category="other" but category_detail missing -- should flag
case1 = {"category": "other", "category_detail": None, "stated_total": 100,
         "calculated_total": 100, "due_date": "2026-11-01"}
errors1 = validate_extraction(case1)
print("Case 1 (other + missing detail):", errors1)
assert len(errors1) == 1 and "category_detail" in errors1[0]

# Case 2: totals mismatch but conflict_detected not set -- should flag
case2 = {"category": "software", "stated_total": 100, "calculated_total": 80,
         "conflict_detected": False, "due_date": "2026-11-01"}
errors2 = validate_extraction(case2)
print("Case 2 (total mismatch, conflict not flagged):", errors2)
assert len(errors2) == 1 and "stated_total" in errors2[0]

# Case 2b: totals mismatch BUT conflict_detected correctly set -- should NOT flag
case2b = {"category": "software", "stated_total": 100, "calculated_total": 80,
          "conflict_detected": True, "due_date": "2026-11-01"}
errors2b = validate_extraction(case2b)
print("Case 2b (total mismatch, correctly flagged):", errors2b)
assert errors2b == []

# Case 3: malformed date -- should flag
case3 = {"category": "travel", "stated_total": 50, "calculated_total": 50,
         "conflict_detected": False, "due_date": "March 3rd"}
errors3 = validate_extraction(case3)
print("Case 3 (bad date format):", errors3)
assert len(errors3) == 1 and "due_date" in errors3[0]

# Case 4: fully valid -- should pass with zero errors
case4 = {"category": "software", "stated_total": 100, "calculated_total": 100,
         "conflict_detected": False, "due_date": "2026-11-01"}
errors4 = validate_extraction(case4)
print("Case 4 (fully valid):", errors4)
assert errors4 == []

print("\nAll validation-retry detection rules fire correctly.")
