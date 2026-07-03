from typing import List
from enum import StrEnum

class BinanceAsset(StrEnum):
    """
    Enum for crypto assets in Binance P2P. Only stablecoins are supported.

    Attributes:
        USDT (str): Tether.
        USDC (str): USD Coin.
        DAI (str): Dai.
    """
    USDT = "USDT"
    USDC = "USDC"
    DAI = "DAI"

    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return self.value

    def asset(self) -> str:
        """Returns the asset name in lowercase."""
        return self.value.lower()
    
    @staticmethod
    def list_currencies() -> List[str]:
        """Returns the list of avaiable assets."""
        return [asset.value for asset in BinanceAsset]
    
    @staticmethod
    def is_valid_currency(asset: str) -> bool:
        """Validate if the crypto asset is avaiable."""
        return asset in BinanceAsset._value2member_map_
    
    @staticmethod
    def from_string(asset_str: str) -> 'BinanceAsset':
        """Validate the strings and returns an BinanceAsset object."""
        try:
            return BinanceAsset(asset_str)
        except ValueError:
            raise ValueError(f"Invalid asset: {asset_str}. Valid options are: {', '.join(BinanceAsset.list_currencies())}")