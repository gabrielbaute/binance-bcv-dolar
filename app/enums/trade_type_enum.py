from typing import List
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
    def list_trades() -> List['TradeType']:
        trade_list = [
            TradeType.BUY,
            TradeType.SELL
        ]
        return trade_list
    
    @staticmethod
    def is_valid_trade(trade: str) -> bool:
        return trade in TradeType.list_trades()
    
    @staticmethod
    def from_string(trade_type_str: str) -> 'TradeType':
        """Validate the strings and returns an TradeType object."""
        try:
            return TradeType(trade_type_str)
        except ValueError:
            raise ValueError(f"Invalid trade type value: {trade_type_str}. Valid options are: {', '.join(TradeType.list_trades())}")