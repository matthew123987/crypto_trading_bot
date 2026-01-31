"""Configuration management for XRP trading bot."""
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env
load_dotenv()


def get_bool_env(key: str, default: bool = False) -> bool:
    """Get boolean value from environment variable.
    
    Args:
        key: Environment variable name
        default: Default value if not set
        
    Returns:
        Boolean value
    """
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')

# Try to load API credentials from ~/.krakenapi first
KRAKEN_API_KEY: str = ""
KRAKEN_API_SECRET: str = ""

kraken_api_file = os.path.expanduser("~/.krakenapi")
if os.path.exists(kraken_api_file):
    # Parse ~/.krakenapi file
    with open(kraken_api_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                if key.strip() == "KRAKEN_API_KEY":
                    KRAKEN_API_KEY = value.strip()
                elif key.strip() == "KRAKEN_API_SECRET":
                    KRAKEN_API_SECRET = value.strip()
else:
    # Fallback to .env file
    KRAKEN_API_KEY = os.getenv("KRAKEN_API_KEY", "")
    KRAKEN_API_SECRET = os.getenv("KRAKEN_API_SECRET", "")


class Config:
    """Configuration class for trading bot settings."""
    
    # API Credentials
    KRAKEN_API_KEY: str = KRAKEN_API_KEY
    KRAKEN_API_SECRET: str = KRAKEN_API_SECRET
    
    # Trading Configuration
    TRADING_PAIR: str = os.getenv("TRADING_PAIR", "XRPUSD")
    BUY_PRICE: float = float(os.getenv("BUY_PRICE", "0.45"))  # Price to buy at
    SELL_PRICE: float = float(os.getenv("SELL_PRICE", "0.60"))  # Price to sell at
    DOLLARS_BUY_AMOUNT: float = float(os.getenv("DOLLARS_BUY_AMOUNT", "100"))  # USD amount to buy
    SELL_ALL: bool = get_bool_env("SELL_ALL", default=False)  # If true, sell all of trading pair crypto after buy fills. If false, sell DOLLARS_BUY_AMOUNT worth
    
    # Backward compatibility
    DOLLARS_BEING_TRADED: float = DOLLARS_BUY_AMOUNT  # Alias for backward compatibility
    
    # Bot Configuration
    CHECK_INTERVAL: int = int(os.getenv("CHECK_INTERVAL", "60"))  # seconds
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Minimum Trade Size (to avoid "volume minimum not met" errors)
    # Set to 0.00001 BTC by default (adjust based on Kraken requirements)
    MIN_CRYPTO_TRADE_SIZE: float = float(os.getenv("MIN_CRYPTO_TRADE_SIZE", "0.00001"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.KRAKEN_API_KEY or not cls.KRAKEN_API_SECRET:
            raise ValueError("KRAKEN_API_KEY and KRAKEN_API_SECRET must be set in ~/.krakenapi or .env file")
        if cls.BUY_PRICE <= 0:
            raise ValueError("BUY_PRICE must be greater than 0")
        if cls.SELL_PRICE <= 0:
            raise ValueError("SELL_PRICE must be greater than 0")
        if cls.DOLLARS_BEING_TRADED <= 0:
            raise ValueError("DOLLARS_BEING_TRADED must be greater than 0")
        return True
