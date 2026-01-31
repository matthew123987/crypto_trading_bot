"""Kraken API client for trading operations."""
import logging
from typing import Dict, Optional
from kraken.spot import Market, Trade, User

logger = logging.getLogger(__name__)


class KrakenClient:
    """Wrapper for Kraken API operations."""
    
    def __init__(self, api_key: str, api_secret: str):
        """Initialize Kraken client with credentials."""
        self.api_key = api_key
        self.api_secret = api_secret
        
        # Initialize Kraken clients
        self.market = Market()
        self.trade = Trade(key=api_key, secret=api_secret)
        self.user = User(key=api_key, secret=api_secret)
        
        logger.info("Kraken client initialized successfully")
    
    def get_current_price(self, pair: str) -> float:
        """
        Get current price for trading pair.
        
        Args:
            pair: Trading pair (e.g., "XRPUSD")
            
        Returns:
            Current price as float
        """
        try:
            ticker = self.market.get_ticker(pair=pair)
            logger.debug("Ticker response: {}".format(ticker))
            
            # Try different pair formats
            price = None
            pair_upper = pair.upper()
            
            # Ticker API response structure varies - handle both with and without "result" wrapper
            result = ticker.get("result", ticker)
            
            # Special case for XBTUSD -> XXBTZUSD
            if pair_upper == "XBTUSD" and "XXBTZUSD" in result:
                price = float(result["XXBTZUSD"]["c"][0])
            # Try exact match first
            elif pair_upper in result:
                price = float(result[pair_upper]["c"][0])
            # Try with X prefix
            elif "X{}".format(pair_upper) in result:
                price = float(result["X{}".format(pair_upper)]["c"][0])
            # Try with ZUSD for USD pairs
            elif pair_upper.replace("USD", "ZUSD") in result:
                price = float(result[pair_upper.replace("USD", "ZUSD")]["c"][0])
            # Try X prefix with ZUSD
            elif "X{}".format(pair_upper.replace("USD", "ZUSD")) in result:
                price = float(result["X{}".format(pair_upper.replace("USD", "ZUSD"))]["c"][0])
            # Fallback: use first available pair
            else:
                first_key = list(result.keys())[0]
                price = float(result[first_key]["c"][0])
                    
            if price:
                logger.debug("Current price for {}: ${}".format(pair, price))
                return price
            else:
                raise ValueError("Invalid response from ticker for {}".format(pair))
        except Exception as e:
            logger.error("Error fetching current price: {}".format(e))
            raise
    
    def get_balance(self) -> Dict[str, float]:
        """
        Get account balance.
        
        Returns:
            Dictionary with asset balances
        """
        try:
            response = self.user.get_account_balance()
            logger.debug("Full API response: {}".format(response))
            
            # Handle both response formats: with or without "result" wrapper
            balance_data = response if "result" not in response else response["result"]
            
            balance = {}
            for asset, amount in balance_data.items():
                balance[asset] = float(amount)
            logger.debug("Current balance: {}".format(balance))
            return balance
        except Exception as e:
            logger.error("Error fetching balance: {}".format(e))
            logger.error("Exception type: {}".format(type(e)))
            raise
    
    def place_limit_buy_order(self, pair: str, volume: float, price: float) -> Optional[str]:
        """
        Place a limit buy order.
        
        Args:
            pair: Trading pair (e.g., "XRPUSD")
            volume: Amount to buy in base currency (crypto)
            price: Limit price in USD
            
        Returns:
            Order transaction ID if successful, None otherwise
        """
        try:
            logger.info("Placing limit buy order: {} {} at ${}".format(volume, pair, price))
            response = self.trade.create_order(
                pair=pair,
                side="buy",
                ordertype="limit",
                volume=str(volume),
                price=str(price)
            )
            
            # Handle both response structures
            if "txid" in response:
                order_id = response["txid"][0] if isinstance(response["txid"], list) else response["txid"]
                logger.info("Limit buy order placed successfully. Order ID: {}".format(order_id))
                return order_id
            elif "result" in response and "txid" in response["result"]:
                order_id = response["result"]["txid"][0] if isinstance(response["result"]["txid"], list) else response["result"]["txid"]
                logger.info("Limit buy order placed successfully. Order ID: {}".format(order_id))
                return order_id
            else:
                logger.error("Failed to place limit buy order: {}".format(response))
                return None
        except Exception as e:
            logger.error("Error placing limit buy order: {}".format(e))
            raise
    
    def place_limit_sell_order(self, pair: str, volume: float, price: float) -> Optional[str]:
        """
        Place a limit sell order.
        
        Args:
            pair: Trading pair (e.g., "XRPUSD")
            volume: Amount to sell in base currency (crypto)
            price: Limit price in USD
            
        Returns:
            Order transaction ID if successful, None otherwise
        """
        try:
            logger.info("Placing limit sell order: {} {} at ${}".format(volume, pair, price))
            response = self.trade.create_order(
                pair=pair,
                side="sell",
                ordertype="limit",
                volume=str(volume),
                price=str(price)
            )
            
            # Handle both response structures
            if "txid" in response:
                order_id = response["txid"][0] if isinstance(response["txid"], list) else response["txid"]
                logger.info("Limit sell order placed successfully. Order ID: {}".format(order_id))
                return order_id
            elif "result" in response and "txid" in response["result"]:
                order_id = response["result"]["txid"][0] if isinstance(response["result"]["txid"], list) else response["result"]["txid"]
                logger.info("Limit sell order placed successfully. Order ID: {}".format(order_id))
                return order_id
            else:
                logger.error("Failed to place limit sell order: {}".format(response))
                return None
        except Exception as e:
            logger.error("Error placing limit sell order: {}".format(e))
            raise
    
    def get_order_status(self, order_id: str) -> Optional[dict]:
        """
        Get order status.
        
        Args:
            order_id: Order transaction ID
            
        Returns:
            Order details if found, None otherwise
        """
        try:
            response = self.user.get_orders_info(txid=order_id)
            if "result" in response:
                orders = response["result"].get("orders", {})
                if order_id in orders:
                    return orders[order_id]
            return None
        except Exception as e:
            logger.error("Error fetching order status: {}".format(e))
            return None
    
    def get_open_orders(self) -> Optional[Dict[str, dict]]:
        """
        Get all open orders.
        
        Returns:
            Dictionary of open orders with order_id as key, order details as value
        """
        try:
            response = self.user.get_open_orders()
            
            # Handle both response formats
            if "result" in response:
                orders = response["result"].get("open", {})
            elif "open" in response:
                orders = response["open"]
            else:
                orders = {}
            return orders
        except Exception as e:
            logger.error("Error fetching open orders: {}".format(e))
            return {}
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order.
        
        Args:
            order_id: Order transaction ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.trade.cancel_order(txid=order_id)
            if "result" in response:
                logger.info("Order {} cancelled successfully".format(order_id))
                return True
            return False
        except Exception as e:
            logger.error("Error cancelling order {}: {}".format(order_id, e))
            raise
