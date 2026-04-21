import re
from decimal import Decimal, InvalidOperation
from typing import Optional

from bot.exceptions import ValidationError

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


def validate_symbol(symbol: str) -> str:
    clean = symbol.strip().upper()
    if not re.fullmatch(r"[A-Z0-9]{5,20}", clean):
        raise ValidationError("Invalid symbol format. Example: BTCUSDT")
    return clean


def validate_side(side: str) -> str:
    clean = side.strip().upper()
    if clean not in VALID_SIDES:
        raise ValidationError("Invalid side. Allowed values: BUY, SELL")
    return clean


def validate_order_type(order_type: str) -> str:
    clean = order_type.strip().upper()
    if clean not in VALID_ORDER_TYPES:
        raise ValidationError("Invalid order type. Allowed values: MARKET, LIMIT")
    return clean


def parse_positive_decimal(value: str, field_name: str) -> Decimal:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ValidationError(f"{field_name} must be a valid number")

    if number <= 0:
        raise ValidationError(f"{field_name} must be greater than 0")
    return number


def decimal_to_str(value: Decimal) -> str:
    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered


def validate_inputs(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str],
) -> dict:
    validated_symbol = validate_symbol(symbol)
    validated_side = validate_side(side)
    validated_type = validate_order_type(order_type)
    validated_qty = parse_positive_decimal(quantity, "quantity")

    validated_price = None
    if validated_type == "LIMIT":
        if price is None:
            raise ValidationError("price is required for LIMIT orders")
        validated_price = parse_positive_decimal(price, "price")

    if validated_type == "MARKET" and price is not None:
        raise ValidationError("price should not be provided for MARKET orders")

    return {
        "symbol": validated_symbol,
        "side": validated_side,
        "order_type": validated_type,
        "quantity": decimal_to_str(validated_qty),
        "price": decimal_to_str(validated_price) if validated_price else None,
    }
