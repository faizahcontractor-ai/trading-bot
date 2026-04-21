import logging
from dataclasses import dataclass
from typing import Dict, Optional

from bot.client import BinanceFuturesClient


@dataclass
class OrderRequest:
    symbol: str
    side: str
    order_type: str
    quantity: str
    price: Optional[str] = None


class OrderService:
    def __init__(self, client: BinanceFuturesClient):
        self.client = client
        self.logger = logging.getLogger(self.__class__.__name__)

    def place(self, req: OrderRequest) -> Dict:
        params = {
            "symbol": req.symbol,
            "side": req.side,
            "type": req.order_type,
            "quantity": req.quantity,
            "newOrderRespType": "RESULT",
        }

        if req.order_type == "LIMIT":
            params["price"] = req.price
            params["timeInForce"] = "GTC"

        response = self.client.place_order(params)

        avg_price = response.get("avgPrice")
        if (not avg_price or avg_price == "0.00000") and response.get("orderId"):
            try:
                order_details = self.client.get_order(req.symbol, int(response["orderId"]))
                response["avgPrice"] = order_details.get("avgPrice", avg_price)
                response["executedQty"] = order_details.get("executedQty", response.get("executedQty"))
                response["status"] = order_details.get("status", response.get("status"))
            except Exception as exc:
                self.logger.warning("Failed to enrich order details: %s", exc)

        return response
