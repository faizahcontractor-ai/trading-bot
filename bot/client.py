import hashlib
import hmac
import logging
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import httpx

from bot.exceptions import BinanceAPIError, BinanceNetworkError


class BinanceFuturesClient:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = "https://testnet.binancefuture.com",
        timeout: float = 15.0,
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.logger = logging.getLogger(self.__class__.__name__)

    def _sign(self, query_string: str) -> str:
        return hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False,
    ) -> Dict[str, Any]:
        params = params.copy() if params else {}

        if signed:
            params.setdefault("timestamp", int(time.time() * 1000))
            params.setdefault("recvWindow", 5000)

        query_string = urlencode(params, doseq=True)
        if signed:
            params["signature"] = self._sign(query_string)

        url = f"{self.base_url}{path}"
        headers = {"X-MBX-APIKEY": self.api_key} if signed else {}

        logged_params = {k: v for k, v in params.items() if k != "signature"}
        self.logger.info(
            "api_request method=%s path=%s params=%s",
            method,
            path,
            logged_params,
        )

        try:
            with httpx.Client(timeout=self.timeout) as client:
                if method == "GET":
                    response = client.get(url, params=params, headers=headers)
                else:
                    response = client.request(method, url, data=params, headers=headers)
        except httpx.RequestError as exc:
            self.logger.exception("network_error path=%s error=%s", path, exc)
            raise BinanceNetworkError(str(exc)) from exc

        try:
            payload = response.json()
        except ValueError:
            payload = {"raw": response.text}

        self.logger.info(
            "api_response method=%s path=%s status=%s payload=%s",
            method,
            path,
            response.status_code,
            payload,
        )

        if response.status_code >= 400:
            raise BinanceAPIError(
                status_code=response.status_code,
                code=payload.get("code") if isinstance(payload, dict) else None,
                message=payload.get("msg", "Unknown API error") if isinstance(payload, dict) else str(payload),
                payload=payload,
            )

        return payload

    def place_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/fapi/v1/order", params=params, signed=True)

    def get_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        return self._request(
            "GET",
            "/fapi/v1/order",
            params={"symbol": symbol, "orderId": order_id},
            signed=True,
        )
