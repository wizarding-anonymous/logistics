import pytest
from decimal import Decimal
from apps.backend.services.payments.service import _calculate_commission

@pytest.mark.parametrize("total, expected_commission", [
    (Decimal("100.00"), Decimal("10.00")),
    (Decimal("123.45"), Decimal("12.345")),
    (Decimal("0"), Decimal("0")),
    (Decimal("999.99"), Decimal("99.999")),
])
def test_calculate_commission(total, expected_commission):
    """
    Tests the commission calculation logic.
    """
    assert _calculate_commission(total) == expected_commission
