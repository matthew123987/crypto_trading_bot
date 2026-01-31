"""Main trading bot for automated cryptocurrency trading."""
import logging
import time
from typing import Optional
from config import Config
from kraken_client import KrakenClient

# Setup logging
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log')
    ],
    force=True
)
logger = logging.getLogger(__name__)

# Add console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)
logger.propagate = False


class CryptoTradingBot:
    """Automated trading bot for cryptocurrency on Kraken."""
    
    def __init__(self):
        """Initialize trading bot."""
        # Validate configuration
        Config.validate()
        
        # Initialize Kraken client
        self.client = KrakenClient(
            api_key=Config.KRAKEN_API_KEY,
            api_secret=Config.KRAKEN_API_SECRET
        )
        
        # Trading configuration
        self.pair = Config.TRADING_PAIR
        self.buy_price = Config.BUY_PRICE
        self.sell_price = Config.SELL_PRICE
        self.dollars_buy_amount = Config.DOLLARS_BUY_AMOUNT
        self.sell_all = Config.SELL_ALL
        self.dollars_being_traded = Config.DOLLARS_BEING_TRADED  # Backward compatibility
        
        # Asset name mapping
        asset_name_map = {
            'XBT': 'BTC',
            'XXBT': 'BTC',
            'XRP': 'XRP',
            'XXRP': 'XRP',
            'ETH': 'ETH',
            'XETH': 'ETH',
            'XXETH': 'ETH'
        }
        
        # Extract base asset code
        base_code = self.pair.replace("USD", "")
        self.base_asset = asset_name_map.get(base_code, base_code.replace("X", "").replace("Z", ""))
        
        # Get Kraken asset codes for API calls
        self.asset_codes = [
            base_code,
            "X{}".format(base_code),
            base_code.replace("X", ""),
            "Z{}".format(base_code.replace("X", "").replace("Z", ""))
        ]
        
        logger.info("Crypto Trading Bot initialized")
        logger.info("Trading pair: {}".format(self.pair))
        logger.info("Base asset: {}".format(self.base_asset))
        logger.info("Buy price: ${}".format(self.buy_price))
        logger.info("Sell price: ${}".format(self.sell_price))
        logger.info("Dollars being traded: ${}".format(self.dollars_being_traded))
    
    def get_open_orders(self) -> dict:
        """Get all open orders for the trading pair.
        
        Returns:
            Dictionary with: {'sell_order': dict, 'buy_order': dict}
        """
        try:
            orders = self.client.get_open_orders()
            
            sell_order = None
            buy_order = None
            
            if orders:
                for order_id, order_info in orders.items():
                    pair_name = order_info.get('descr', {}).get('pair', '')
                    order_type = order_info.get('descr', {}).get('type', '')
                    
                    if pair_name == self.pair:
                        order_info['order_id'] = order_id
                        if order_type == 'sell':
                            sell_order = order_info
                        elif order_type == 'buy':
                            buy_order = order_info
            
            return {'sell_order': sell_order, 'buy_order': buy_order}
            
        except Exception as e:
            logger.error("Error getting open orders: {}".format(e))
            return {'sell_order': None, 'buy_order': None}
    
    def get_balance(self) -> dict:
        """Get account balances.
        
        Returns:
            Dictionary with: {'crypto_amount': float, 'usd_balance': float}
        """
        try:
            balance = self.client.get_balance()
            
            # Get crypto amount
            crypto_amount = 0
            for code in self.asset_codes:
                if code in balance:
                    crypto_amount = float(balance[code])
                    break
            
            # Get USD balance
            usd_balance = balance.get("ZUSD", 0) or balance.get("USD", 0)
            usd_balance = float(usd_balance)
            
            return {'crypto_amount': crypto_amount, 'usd_balance': usd_balance}
            
        except Exception as e:
            logger.error("Error getting balance: {}".format(e))
            return {'crypto_amount': 0, 'usd_balance': 0}
    
    def place_buy_limit_order(self) -> Optional[str]:
        """Place a limit buy order.
        
        Returns:
            Order ID if successful, None otherwise
        """
        try:
            crypto_amount = self.dollars_being_traded / self.buy_price
            
            logger.info("=== PLACING BUY ORDER ===")
            logger.info("Amount: ${}".format(self.dollars_being_traded))
            logger.info("Crypto amount: {} {}".format(crypto_amount, self.base_asset))
            logger.info("Limit price: ${}".format(self.buy_price))
            
            order_id = self.client.place_limit_buy_order(
                pair=self.pair,
                volume=crypto_amount,
                price=self.buy_price
            )
            
            if order_id:
                logger.info("✓✓✓ Limit buy order placed ✓✓✓")
                logger.info("✓ Order ID: {}".format(order_id))
                return order_id
            else:
                logger.error("✗ Failed to place limit buy order")
                return None
                
        except Exception as e:
            error_msg = str(e)
            if "Insufficient funds" in error_msg or "EOrder:Insufficient" in error_msg:
                logger.warning("✗ Insufficient funds to place buy order")
                return None
            else:
                logger.error("✗ Error placing limit buy order: {}".format(e))
                return None
    
    def place_sell_limit_order(self, crypto_amount: float) -> Optional[str]:
        """Place a limit sell order.
        
        Args:
            crypto_amount: Amount of crypto to sell
            
        Returns:
            Order ID if successful, None otherwise
        """
        try:
            # Check if amount meets minimum trade size requirement
            if crypto_amount < Config.MIN_CRYPTO_TRADE_SIZE:
                logger.info("ℹ Cannot place sell order: amount ({:.8f} {}) is below minimum trade size ({:.8f} {})".format(
                    crypto_amount, self.base_asset, Config.MIN_CRYPTO_TRADE_SIZE, self.base_asset))
                logger.info("ℹ Skipping sell order - amount too small for Kraken minimum volume requirement")
                return None
            
            logger.info("=== PLACING SELL ORDER ===")
            logger.info("Amount: {} {}".format(crypto_amount, self.base_asset))
            logger.info("Limit price: ${}".format(self.sell_price))
            
            order_id = self.client.place_limit_sell_order(
                pair=self.pair,
                volume=crypto_amount,
                price=self.sell_price
            )
            
            if order_id:
                logger.info("✓✓✓ Limit sell order placed ✓✓✓")
                logger.info("✓ Order ID: {}".format(order_id))
                return order_id
            else:
                logger.error("✗ Failed to place limit sell order")
                return None
                
        except Exception as e:
            logger.error("✗ Error placing limit sell order: {}".format(e))
            return None
    
    def get_current_price(self) -> Optional[float]:
        """Get current price for the trading pair.
        
        Returns:
            Current price as float, None if error
        """
        try:
            return self.client.get_current_price(self.pair)
        except Exception as e:
            logger.warning("Could not fetch current price: {}".format(e))
            return None
    
    def run(self):
        """Main bot loop."""
        logger.info("=" * 60)
        logger.info("Starting Crypto Trading Bot (LIMIT ORDERS)")
        logger.info("=" * 60)
        
        iteration = 0
        
        try:
            while True:
                iteration += 1
                logger.info("=" * 60)
                logger.info("--- Iteration {} ---".format(iteration))
                logger.info("=" * 60)
                
                try:
                    # Step 1: Check if there is a sell position with trading pair
                    orders = self.get_open_orders()
                    sell_order = orders['sell_order']
                    buy_order = orders['buy_order']
                    
                    if sell_order:
                        # Sell position exists - wait for it to sell
                        order_id = sell_order.get('order_id', 'Unknown')
                        price = float(sell_order.get('descr', {}).get('price', '0'))
                        volume = float(sell_order.get('vol', '0'))
                        total = price * volume
                        
                        buy_amount = self.dollars_being_traded / self.buy_price
                        
                        logger.info("Found open SELL order for {} ({}) at price ${:.2f} for {:.8f} {}, total trade worth ${:.2f}".format(
                            self.pair, self.base_asset, price, volume, self.base_asset, total))
                        logger.info("Order ID: {}".format(order_id))
                        logger.info("Waiting for sell order to fill...")
                        logger.info("If sell order fills, I will create a buy limit order at price ${:.2f} for {:.8f} {}, total trade worth ${:.2f}".format(
                            self.buy_price, buy_amount, self.base_asset, self.dollars_being_traded))
                    
                    # Step 2: If there is NOT a sell position, check if there is a buy position
                    elif buy_order:
                        # Buy position exists - wait for it to buy
                        order_id = buy_order.get('order_id', 'Unknown')
                        price = float(buy_order.get('descr', {}).get('price', '0'))
                        volume = float(buy_order.get('vol', '0'))
                        total = price * volume
                        
                        # Calculate sell amount based on SELL_ALL setting
                        if self.sell_all:
                            # Sell all of trading pair crypto (calculate what we WILL have after buy fills)
                            sell_amount = volume  # The amount being bought
                            sell_total = sell_amount * self.sell_price
                        else:
                            # Sell DOLLARS_BUY_AMOUNT worth
                            sell_amount = self.dollars_being_traded / self.sell_price
                            sell_total = self.dollars_being_traded
                        
                        logger.info("Found open BUY order for {} ({}) at price ${:.2f} for {:.8f} {}, total trade worth ${:.2f}".format(
                            self.pair, self.base_asset, price, volume, self.base_asset, total))
                        logger.info("Order ID: {}".format(order_id))
                        logger.info("Waiting for buy order to fill...")
                        logger.info("If buy order fills, I will create a sell limit order at price ${:.2f} for {:.8f} {}, total trade worth ${:.2f} - SELL_ALL={} has been set".format(
                            self.sell_price, sell_amount, self.base_asset, sell_total, self.sell_all))
                    
                    # Step 3: If there is NEITHER a sell or buy position
                    else:
                        balance = self.get_balance()
                        
                        # Step 3.5: Check if there is crypto in account (no orders but have crypto)
                        if balance['crypto_amount'] > 0:
                            # Have crypto - sell it immediately at sell_price
                            if self.sell_all:
                                # Sell all of trading pair crypto
                                sell_amount = balance['crypto_amount']
                                sell_total = sell_amount * self.sell_price
                            else:
                                # Sell DOLLARS_BUY_AMOUNT worth
                                sell_amount = self.dollars_being_traded / self.sell_price
                                sell_total = self.dollars_being_traded
                            
                            # Check if amount meets minimum trade size before logging
                            if sell_amount >= Config.MIN_CRYPTO_TRADE_SIZE:
                                # Amount is sufficient - log and place sell order
                                logger.info("No open orders but have {:.8f} {} in account".format(
                                    balance['crypto_amount'], self.base_asset))
                                if self.sell_all:
                                    logger.info("SELL_ALL=True - placing sell order for ALL {} at ${:.2f} for {:.8f} {}, total trade worth ${:.2f} - SELL_ALL={} has been set".format(
                                        self.base_asset, self.sell_price, sell_amount, self.base_asset, sell_total, self.sell_all))
                                else:
                                    logger.info("SELL_ALL=False - placing sell order for ${:.2f} worth: {:.8f} {} at ${:.2f}, total trade worth ${:.2f} - SELL_ALL={} has been set".format(
                                        self.dollars_being_traded, sell_amount, self.base_asset, self.sell_price, sell_total, self.sell_all))
                                order_id = self.place_sell_limit_order(sell_amount)
                            else:
                                # Amount is too small - skip sell order without logging "placing" message
                                logger.info("ℹ Cannot place sell order: amount ({:.8f} {}) is below minimum trade size ({:.8f} {})".format(
                                    sell_amount, self.base_asset, Config.MIN_CRYPTO_TRADE_SIZE, self.base_asset))
                                logger.info("ℹ Skipping sell order - amount too small for Kraken minimum volume requirement")
                                order_id = None
                            
                            # If sell order was skipped (amount too small) or failed, check for USD to buy
                            if order_id is None and balance['usd_balance'] >= self.dollars_being_traded:
                                logger.info("Sell order skipped/not placed - checking for available USD to buy...")
                                logger.info("✓ USD balance: ${:.2f}".format(balance['usd_balance']))
                                self.place_buy_limit_order()
                        
                        # Step 4: Check if there is USD available for dollars_being_traded_amount
                        elif balance['usd_balance'] >= self.dollars_being_traded:
                            # Have USD - place buy order
                            logger.info("No open orders and no {} in account".format(self.base_asset))
                            logger.info("✓ USD balance: ${:.2f}".format(balance['usd_balance']))
                            self.place_buy_limit_order()
                        
                        # Step 5: No crypto, no USD - wait
                        else:
                            logger.warning("No open orders and no {} in account".format(self.base_asset))
                            logger.warning("USD balance: ${:.2f} - need ${:.2f} to trade".format(
                                balance['usd_balance'], self.dollars_being_traded))
                            logger.warning("Waiting for funds...")
                    
                    # Show current price and USD balance
                    current_price = self.get_current_price()
                    balance = self.get_balance()
                    if current_price:
                        logger.info("Current {} Price: ${:.4f}. ${:.2f} USD currently in account".format(
                            self.base_asset, current_price, balance['usd_balance']))
                    
                except Exception as e:
                    logger.error("Error in trading iteration: {}".format(e))
                    logger.info("Continuing to next iteration...")
                
                # Step 5: Repeat all above continually
                logger.info("Waiting {} seconds...".format(Config.CHECK_INTERVAL))
                time.sleep(Config.CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            logger.info("\n" + "=" * 60)
            logger.info("Bot stopped by user")
            logger.info("=" * 60)
            
            # Cancel any open orders
            orders = self.get_open_orders()
            if orders['sell_order']:
                logger.info("Cancelling open sell order: {}".format(orders['sell_order']['order_id']))
                self.client.cancel_order(orders['sell_order']['order_id'])
            if orders['buy_order']:
                logger.info("Cancelling open buy order: {}".format(orders['buy_order']['order_id']))
                self.client.cancel_order(orders['buy_order']['order_id'])
            
            # Final balance
            balance = self.get_balance()
            logger.info("Final {} Balance: {:.8f}".format(self.base_asset, balance['crypto_amount']))
            logger.info("Final USD Balance: ${:.2f}".format(balance['usd_balance']))
            
        except Exception as e:
            logger.error("Fatal error in bot: {}".format(e))
            raise


def main():
    """Main entry point."""
    try:
        bot = CryptoTradingBot()
        bot.run()
    except Exception as e:
        logger.error("Failed to start bot: {}".format(e))


if __name__ == "__main__":
    main()
