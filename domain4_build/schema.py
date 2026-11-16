"""
Task 4.3 — Invoice extraction schema demonstrating:
  - required fields (always expected to exist on any invoice)
  - optional/nullable fields (prevents fabrication when source lacks info)
  - enum with "other" + freeform detail (extensible categorisation)
  - "unclear" value for genuinely ambiguous cases

Task 4.4 — calculated_total alongside stated_total (self-correction flow),
plus conflict_detected for other inconsistencies.
"""

EXTRACT_INVOICE_TOOL = {
    "name": "extract_invoice",
    "description": (
        "Extracts structured data from an invoice document. Required fields "
        "must always be present on a valid invoice. Nullable fields should "
        "be left null if the source document does not state that "
        "information explicitly -- NEVER invent a value to fill a field."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            # --- Required fields: every real invoice has these ---
            "invoice_number": {"type": "string"},
            "vendor_name": {"type": "string"},
            "stated_total": {
                "type": "number",
                "description": "The total amount as explicitly stated on the invoice.",
            },
            "calculated_total": {
                "type": "number",
                "description": (
                    "Sum of all line item amounts, calculated by YOU from the "
                    "line items you extracted. Must be computed independently "
                    "of stated_total, not copied from it."
                ),
            },
            "line_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "amount": {"type": "number"},
                    },
                    "required": ["description", "amount"],
                },
            },

            # --- Optional / nullable: source may not contain these ---
            "tax_id": {
                "type": ["string", "null"],
                "description": (
                    "Vendor tax ID if explicitly stated. Use null if the "
                    "document does not mention a tax ID -- do NOT invent one."
                ),
            },
            "due_date": {
                "type": ["string", "null"],
                "description": "ISO 8601 date (YYYY-MM-DD) if stated, else null.",
            },

            # --- Enum with "other" escape hatch ---
            "category": {
                "type": "string",
                "enum": ["software", "consulting", "hardware", "travel", "other"],
                "description": "Best-fit category. Use 'other' if none fit.",
            },
            "category_detail": {
                "type": ["string", "null"],
                "description": (
                    "Required (non-null) only when category is 'other' -- a "
                    "short freeform description of what the category actually is."
                ),
            },

            # --- "unclear" enum value for ambiguous cases ---
            "payment_status": {
                "type": "string",
                "enum": ["paid", "unpaid", "partially_paid", "unclear"],
                "description": (
                    "Use 'unclear' if the document does not explicitly state "
                    "payment status -- do not guess based on indirect cues."
                ),
            },

            # --- Self-correction / conflict detection (Task 4.4) ---
            "conflict_detected": {
                "type": "boolean",
                "description": (
                    "True if calculated_total and stated_total differ, or if "
                    "any other internal inconsistency was noticed in the source."
                ),
            },
            "conflict_detail": {
                "type": ["string", "null"],
                "description": "If conflict_detected is true, briefly describe the conflict.",
            },
        },
        "required": [
            "invoice_number", "vendor_name", "stated_total", "calculated_total",
            "line_items", "category", "payment_status", "conflict_detected",
        ],
    },
}
