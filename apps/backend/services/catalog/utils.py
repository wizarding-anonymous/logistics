from decimal import Decimal

def format_price(price: Decimal, currency: str) -> str:
    """
    Formats a price and currency into a human-readable string.
    """
    return f"{price:,.2f} {currency}"
