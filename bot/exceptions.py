class ValidationError(Exception):
    """Raised when CLI/user input validation fails."""


class BinanceNetworkError(Exception):
    """Raised for network transport failures."""


class BinanceAPIError(Exception):
    """Raised when Binance API returns a non-2xx response."""

    def __init__(self, status_code: int, code=None, message: str = "", payload=None):
        super().__init__(f"Binance API error (HTTP {status_code}, code={code}): {message}")
        self.status_code = status_code
        self.code = code
        self.message = message
        self.payload = payload
