from enum import StrEnum

class TradeType(StrEnum):
    """
    Enum for trade types in Binance P2P platform.

    Attributes:
        BUY (str): Buy trade type.
        SELL (str): Sell trade type.
    """
    BUY = "BUY"
    SELL = "SELL"

    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return self.value
    
    @staticmethod
    def list_trades() -> list:
        return [trade.value for trade in TradeType]
    
    @staticmethod
    def is_valid_trade(trade: str) -> bool:
        return trade in TradeType.list_trades()