import pytest
from decimal import Decimal
from apps.backend.services.catalog.utils import format_price

@pytest.mark.parametrize("price, currency, expected", [
    (Decimal("1234.56"), "USD", "1,234.56 USD"),
    (Decimal("999"), "EUR", "999.00 EUR"),
    (Decimal("0.5"), "RUB", "0.50 RUB"),
])
def test_format_price(price, currency, expected):
    assert format_price(price, currency) == expected
