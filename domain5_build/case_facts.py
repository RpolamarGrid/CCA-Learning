"""
Task 5.1 — persistent case facts block.

This is NOT conversation history. It is a structured record of hard
transactional facts that is injected VERBATIM into every prompt sent to
every subagent and the coordinator itself. It is never summarised, never
condensed -- the whole point is that it survives exactly as captured,
regardless of how long the surrounding conversation gets.
"""

import json


class CaseFacts:
    def __init__(self, customer_name, order_id, refund_amount, order_date, complaint):
        self.customer_name = customer_name
        self.order_id = order_id
        self.refund_amount = refund_amount
        self.order_date = order_date
        self.complaint = complaint

    def as_block(self) -> str:
        """Verbatim structured block -- this exact text is what gets
        injected into every prompt. Never paraphrased, never summarised."""
        return (
            "=== CASE FACTS (verbatim, do not paraphrase or round) ===\n"
            f"Customer: {self.customer_name}\n"
            f"Order ID: {self.order_id}\n"
            f"Refund amount requested: ${self.refund_amount:.2f}\n"
            f"Order date: {self.order_date}\n"
            f"Customer's stated complaint: \"{self.complaint}\"\n"
            "=== END CASE FACTS ===\n"
        )

    def as_dict(self) -> dict:
        return {
            "customer_name": self.customer_name,
            "order_id": self.order_id,
            "refund_amount": self.refund_amount,
            "order_date": self.order_date,
            "complaint": self.complaint,
        }
