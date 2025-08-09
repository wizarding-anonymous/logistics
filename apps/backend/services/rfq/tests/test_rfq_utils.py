import pytest
from apps.backend.services.rfq.utils import generate_rfq_summary
from apps.backend.services.rfq.models import RFQ

def test_generate_rfq_summary():
    """
    Tests the summary generation for a mock RFQ object.
    """
    # Create a mock RFQ object. We don't need a real SQLAlchemy model instance for this.
    class MockRFQ:
        def __init__(self, origin, dest, cargo):
            self.origin_address = origin
            self.destination_address = dest
            self.cargo_description = cargo

    mock_rfq = MockRFQ(
        origin="Port of Hamburg",
        dest="Port of Shanghai",
        cargo="2 tons of German machinery"
    )

    expected_summary = "RFQ from Port of Hamburg to Port of Shanghai for '2 tons of German machinery'."

    assert generate_rfq_summary(mock_rfq) == expected_summary

def test_generate_rfq_summary_invalid_input():
    """
    Tests the summary generation with invalid input.
    """
    assert generate_rfq_summary(None) == "Invalid RFQ"
