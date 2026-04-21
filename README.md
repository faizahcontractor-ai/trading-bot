# Binance Futures Testnet Trading Bot (Python)

A simplified Python trading bot for **Binance Futures Testnet (USDT-M)**.

## Features
- Places `MARKET` and `LIMIT` orders
- Supports `BUY` and `SELL`
- CLI input with validation
- Structured code (client/API, orders, validators, CLI)
- Request/response/error logging to file
- Exception handling for validation, API, and network errors

## Project Structure

```text
trading_bot_task/
  bot/
    __init__.py
    client.py
    exceptions.py
    logging_config.py
    orders.py
    validators.py
  logs/
  cli.py
  .env.example
  README.md
  requirements.txt
```

## Setup

1. Create Binance Futures Testnet account and API keys.
2. Clone/download this project.
3. Create and activate venv:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Configure environment variables:

```bash
cp .env.example .env
```

Add your credentials in `.env`:
- `BINANCE_API_KEY`
- `BINANCE_API_SECRET`

Base URL used by default:
- `https://testnet.binancefuture.com`

## How to Run

### MARKET order (example)

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### LIMIT order (example)

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 90000
```

### Optional base URL override

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --base-url https://testnet.binancefuture.com
```

## Output

The app prints:
- Order request summary
- Order response details (`orderId`, `status`, `executedQty`, `avgPrice` if available)
- Clear success/failure message

## Logs

Log file path:
- `logs/trading_bot.log`

After running one MARKET and one LIMIT order, submit that log file as part of your deliverables.

## Assumptions
- Account is set up correctly on Binance Futures Testnet (USDT-M).
- Trading pair is valid for USDT-M futures (e.g., `BTCUSDT`).
- Quantity/price values are acceptable for the selected symbol filters.
