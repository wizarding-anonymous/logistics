from . import models

def generate_rfq_summary(rfq: models.RFQ) -> str:
    """
    Generates a human-readable summary string for an RFQ.
    """
    if not rfq:
        return "Invalid RFQ"

    summary = (
        f"RFQ from {rfq.origin_address} to {rfq.destination_address} "
        f"for '{rfq.cargo_description}'."
    )
    return summary
