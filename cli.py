import argparse
import logging
import os
import sys

from dotenv import load_dotenv

from bot.client import BinanceFuturesClient
from bot.exceptions import BinanceAPIError, BinanceNetworkError, ValidationError
from bot.logging_config import setup_logging
from bot.orders import OrderRequest, OrderService
from bot.validators import validate_inputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Place Binance Futures Testnet orders")
    parser.add_argument("--symbol", required=True, help="Trading symbol, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, help="BUY or SELL")
    parser.add_argument("--type", required=True, dest="order_type", help="MARKET or LIMIT")
    parser.add_argument("--quantity", required=True, help="Order quantity")
    parser.add_argument("--price", required=False, help="Price (required for LIMIT)")
    parser.add_argument(
        "--base-url",
        default="https://testnet.binancefuture.com",
        help="Binance Futures Testnet base URL",
    )
    return parser


def print_summary(validated: dict) -> None:
    print("\n=== Order Request Summary ===")
    print(f"Symbol     : {validated['symbol']}")
    print(f"Side       : {validated['side']}")
    print(f"Order Type : {validated['order_type']}")
    print(f"Quantity   : {validated['quantity']}")
    if validated["order_type"] == "LIMIT":
        print(f"Price      : {validated['price']}")


def print_response(response: dict) -> None:
    print("\n=== Order Response ===")
    print(f"orderId     : {response.get('orderId')}")
    print(f"status      : {response.get('status')}")
    print(f"executedQty : {response.get('executedQty')}")
    print(f"avgPrice    : {response.get('avgPrice')}")


def main() -> int:
    setup_logging("logs/trading_bot.log")
    logger = logging.getLogger("cli")
    load_dotenv()

    args = build_parser().parse_args()

    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        print("Error: BINANCE_API_KEY and BINANCE_API_SECRET must be set in environment.")
        return 2

    try:
        validated = validate_inputs(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )

        print_summary(validated)

        client = BinanceFuturesClient(
            api_key=api_key,
            api_secret=api_secret,
            base_url=args.base_url,
        )
        service = OrderService(client)

        req = OrderRequest(
            symbol=validated["symbol"],
            side=validated["side"],
            order_type=validated["order_type"],
            quantity=validated["quantity"],
            price=validated["price"],
        )

        response = service.place(req)
        print_response(response)

        print("\nSUCCESS: Order placed successfully.")
        return 0

    except ValidationError as exc:
        logger.error("validation_error: %s", exc)
        print(f"\nFAILED: Validation error -> {exc}")
        return 3
    except BinanceAPIError as exc:
        logger.error("api_error: %s payload=%s", exc, exc.payload)
        print(f"\nFAILED: Binance API error -> {exc}")
        return 4
    except BinanceNetworkError as exc:
        logger.error("network_error: %s", exc)
        print(f"\nFAILED: Network error -> {exc}")
        return 5
    except Exception as exc:
        logger.exception("unexpected_error: %s", exc)
        print(f"\nFAILED: Unexpected error -> {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
