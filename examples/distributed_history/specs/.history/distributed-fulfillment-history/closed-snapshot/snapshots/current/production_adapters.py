"""Production adapters for current-model ticket workflow cases.

Add one small adapter per modeled boundary. Each adapter should materialize the
case pre-state, call the production boundary, observe production state, and
refine that observation back to the generated case shape.
"""

from __future__ import annotations


class ScaffoldedTicketAdapter:
    """Placeholder adapter documenting the expected shape."""

    def can_run(self, case):
        return False, "replace ScaffoldedTicketAdapter with a ticket-specific adapter"
