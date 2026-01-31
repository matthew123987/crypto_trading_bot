# crypto_trading_bot
Crypto trading bot that buys and sells automatically 24/7 based on configured thresholds to get profit.

# Cryptocurrency Automated Trading Bot for Kraken

An automated trading bot that executes buy/sell orders for any cryptocurrency on Kraken based on configurable price thresholds. 

## Features

- **Multi-Currency Support**: Trade XRP, Bitcoin, Ethereum, or any Kraken-supported cryptocurrency
- **Automated Trading**: Automatically buys when price drops to your buy threshold and sells when it reaches your target price
- **Configurable Thresholds**: Set your own buy price and sell price
- **Smart State Detection**: Automatically detects open orders, USD balance, or crypto holdings
- **Fixed USD Position**: Trade a fixed USD amount each time (e.g., $100 worth of any cryptocurrency)
- **Real-time Monitoring**: Checks price at configurable intervals
- **Comprehensive Logging**: Logs all trading activities to both console and file

## Supported Cryptocurrencies

The bot automatically detects the asset from your trading pair and works with:

- **XRP**: Use `TRADING_PAIR=XRPUSD`
- **Bitcoin**: Use `TRADING_PAIR=XBTUSD` or `TRADING_PAIR=BTCUSD`
- **Ethereum**: Use `TRADING_PAIR=ETHUSD`
- **Litecoin**: Use `TRADING_PAIR=LTCUSD`
- **And more**: Any Kraken-supported trading pair ending in USD

## Prerequisites

- Python 3.7 or higher
- Kraken account with API access
- USD and crypto balances in your Kraken account (depending on start mode)
- Ubuntu/Linux system (works on desktop, laptop, or cloud servers)

## Platform Support

### Ubuntu Laptop/Desktop
Fully supported - works on Ubuntu systems

The bot will run:
- When your laptop is locked
- When you close terminal windows
- In the background while you do other work

Use **Background Mode** (run_bot.sh) or **Systemd Mode** (auto-start service) to keep it running 24/7.

### AWS EC2 / Cloud Servers

When you're ready to move to AWS EC2:
1. Launch an Ubuntu EC2 instance (t3.micro or t3.small is sufficient)
2. SSH into the instance
3. Clone or upload the bot files
4. Install dependencies: `pip3 install -r requirements.txt`
5. Configure `.env` with your Kraken API keys
6. Use Systemd mode for auto-restart on boot
7. Close your SSH session - bot keeps running!

**Benefits of EC2:**
- Bot runs 24/7 without your laptop
- Automatic restart if instance reboots
- Access logs from anywhere via SSH
- Low cost (~$5-15/month for t3.small)

## Setup

### 1. Clone or Download

Navigate to the bot directory:

```bash
cd /home/matthew/Documents/code/trading/crypto_trading_bot
```

### 2. Install Dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 3. Get Kraken API Credentials

1. Log in to your Kraken account
2. Go to Settings > API
3. Create a new API key
4. Grant following permissions:
   - **Funds**: Query (check balances)
   - **Orders and trades**: Query open orders & trades, Create & modify orders, Cancel & close orders
5. Copy your API Key and API Secret
6. Create `~/.krakenapi` file in your home directory:

```bash
echo "KRAKEN_API_KEY=your_api_key_here" > ~/.krakenapi
echo "KRAKEN_API_SECRET=your_api_secret_here" >> ~/.krakenapi
chmod 600 ~/.krakenapi
```

### 4. Configure Bot

Copy example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Kraken API Credentials
# (Loaded from ~/.krakenapi)
# KRAKEN_API_KEY and KRAKEN_API_SECRET should be in ~/.krakenapi file

# Trading Configuration
TRADING_PAIR=XBTUSD       # Trading pair (e.g., XRPUSD, XBTUSD for Bitcoin, ETHUSD for Ethereum)
BUY_PRICE=87841.00       # Price to buy at (USD per unit)
SELL_PRICE=89157.00      # Price to sell at (USD per unit)
DOLLARS_BEING_TRADED=100  # USD amount to buy/sell each trade

# Bot Configuration
CHECK_INTERVAL=60         # Time between price checks (seconds)
LOG_LEVEL=INFO            # Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## How It Works

### Trading Logic

The bot uses **smart state detection** and **limit orders** for precise trading:

1. **Check for Open Orders**:
   - If a sell order exists: Wait for it to fill, then place a buy limit order at BUY_PRICE
   - If a buy order exists: Wait for it to fill, then place a sell limit order at SELL_PRICE

2. **Check for Crypto Holdings**:
   - If you have crypto: Place a sell limit order at SELL_PRICE
   - Wait for order to fill, then place buy order at BUY_PRICE

3. **Check for USD Balance**:
   - If you have enough USD: Place a buy limit order at BUY_PRICE
   - Wait for order to fill, then place sell order at SELL_PRICE

4. **Continuous Loop**:
   - Repeat checks every CHECK_INTERVAL seconds
   - Automatically adapts to account state changes
   - Handles orders placed outside the bot

### Order Types

The bot uses **limit orders** for better price control:
- **Buy Orders**: Placed at BUY_PRICE (waits for price to drop)
- **Sell Orders**: Placed at SELL_PRICE (waits for price to rise)
- No slippage - you get exactly your target price


### Start Bot

```bash
python trading_bot.py
```

The bot will:
1. Connect to Kraken API
2. Display initial account balance
3. Detect your trading pair and asset type
4. Start monitoring price
5. Execute trades based on your configuration
6. Log all activities to `trading_bot.log`

### Stop Bot

Press `Ctrl+C` to stop the bot. It will:
1. Display final account status
2. Warn you if you're still holding a position
3. Close gracefully

## Running Modes

### 1. Foreground Mode (Testing)

Run the bot in your terminal:

```bash
python3 trading_bot.py
```

**Best for:**
- Testing and debugging
- Initial setup verification
- Short-term manual trading

**Note:** Bot stops when you close the terminal.

### 2. Background Mode (Manual Control)

Run the bot in the background:

```bash
./run_bot.sh
```

The bot will:
- Run in the background
- Continue even if you close the terminal
- Keep running while your laptop is locked

**Stop the bot:**

```bash
./stop_bot.sh
```

**View logs:**

```bash
tail -f trading_bot.log
```

**Best for:**
- Running on your laptop/desktop
- Manual control
- Testing before using systemd

### 3. Systemd Mode (Auto-Restart + Anti-Suspension)

Run as a system service with auto-restart and prevent system suspension:

**About the Inhibitor Service:**
The bot includes a companion service (`crypto-trading-bot-inhibitor.service`) that prevents your system from suspending or sleeping while the bot is running. This is essential for laptops/desktops because:
- The bot uses `time.sleep()` to wait between price checks
- When you lock your computer, the system may suspend the bot process
- This causes the 60-second wait to extend to several minutes
- The inhibitor ensures the bot maintains accurate timing even when the screen is locked

**Install services:**

```bash
# Copy the main bot service
sudo cp crypto-trading-bot.service /etc/systemd/system/

# Copy the inhibitor service (prevents system suspension)
sudo cp crypto-trading-bot-inhibitor.service /etc/systemd/system/

# Reload systemd to recognize new services
sudo systemctl daemon-reload

# Enable both services to start on boot
sudo systemctl enable crypto-trading-bot-inhibitor.service
sudo systemctl enable crypto-trading-bot.service
```

**Start/Stop/Restart:**

```bash
# Start both services
sudo systemctl start crypto-trading-bot-inhibitor.service crypto-trading-bot.service

# Stop both services
sudo systemctl stop crypto-trading-bot-inhibitor.service crypto-trading-bot.service

# Restart both services
sudo systemctl restart crypto-trading-bot-inhibitor.service crypto-trading-bot.service
```

**Check status:**

```bash
# Check both services
sudo systemctl status crypto-trading-bot-inhibitor.service crypto-trading-bot.service

# Verify the sleep inhibitor is active
sudo loginctl show-session $(loginctl | grep $(whoami) | awk '{print $1}') -p ActiveInhibitors
```

Expected inhibitor output:
```
ActiveInhibitors=who:root:what:sleep:why:"Trading bot is running - do not suspend"
```

**View logs:**

```bash
# View systemd logs for both services
sudo journalctl -u crypto-trading-bot.service -f
sudo journalctl -u crypto-trading-bot-inhibitor.service -f

# Or view the bot's log file
tail -f trading_bot.log
```

**Benefits:**
- Automatic restart if bot crashes
- Automatic start on system boot
- **System won't suspend while bot is running** - accurate 60-second intervals even when locked
- 24/7 operation without keeping terminal open
- Professional deployment
- No timing issues when laptop is locked or screen saver activates

**Best for:**
- Production trading
- 24/7 operation on laptops/desktops
- Cloud servers (AWS EC2, etc.)
- Unattended operation
- When you need accurate timing regardless of system state

**Note:** The `./stop_bot.sh` script will detect if systemd is managing the bot and provide instructions to use systemctl commands instead.

## Monitoring

### Console Output

The bot displays real-time information:
- Current crypto price
- Trading signals (BUY/SELL)
- Position status
- Account balances
- Profit/loss calculations

### Log File

All activities are logged to `trading_bot.log`:
- Trade executions
- Errors and warnings
- Account status updates

## Configuration Options

| Parameter | Description | Example Values |
|-----------|-------------|----------------|
| `KRAKEN_API_KEY` | Your Kraken API key (in ~/.krakenapi) | `ABCDE-FGHIJ-KLMNO` |
| `KRAKEN_API_SECRET` | Your Kraken API secret (in ~/.krakenapi) | `abc123...xyz789` |
| `TRADING_PAIR` | Trading pair | `XRPUSD`, `XBTUSD`, `ETHUSD`, `LTCUSD` |
| `BUY_PRICE` | Buy limit order price | `0.45` (XRP), `40000` (BTC), `2000` (ETH) |
| `SELL_PRICE` | Sell limit order price | `0.60` (XRP), `45000` (BTC), `2500` (ETH) |
| `DOLLARS_BEING_TRADED` | USD amount to buy/sell each trade | `100`, `500`, `1000` (any amount in USD) |
| `CHECK_INTERVAL` | Seconds between price checks | `60` (1 minute), `300` (5 minutes) |
| `LOG_LEVEL` | Logging verbosity | `INFO`, `DEBUG`, `WARNING` |

## Important Notes

### Risk Warnings

⚠️ **TRADING CRYPTOCURRENCY INVOLVES SIGNIFICANT RISK**

- This bot does not guarantee profits
- You can lose your entire investment
- Past performance does not guarantee future results
- Test with small amounts first
- Never trade money you cannot afford to lose

### Best Practices

1. **Start Small**: Begin with small USD amounts (e.g., $10-100)
2. **Test Thoroughly**: Run with minimal funds first to verify configuration
3. **Monitor Regularly**: Check the bot periodically, especially when starting
4. **Set Reasonable Prices**: Use realistic buy/sell prices based on market analysis
5. **Keep Logs**: Review `trading_bot.log` regularly
6. **Secure Your Keys**: Never commit `.env` to version control
7. **Understand Your Asset**: Different cryptocurrencies have different volatilities
8. **Calculate Risk**: Remember you're trading a fixed USD amount, not a fixed number of units

### Limitations

- Only supports simple threshold-based trading
- No technical indicators or advanced strategies
- No stop-loss orders (add manually if needed)
- No paper trading mode
- Trades a fixed USD amount (crypto units vary based on price)

### API Rate Limits

Kraken has API rate limits. The bot respects these by:
- Using reasonable check intervals (default: 60 seconds)
- Handling rate limit errors gracefully
- Continuing operation after temporary API errors

## Troubleshooting

### Authentication Errors

```
ValueError: KRAKEN_API_KEY and KRAKEN_API_SECRET must be set in ~/.krakenapi or .env file
```

**Solution**: Ensure you've created `~/.krakenapi` file with correct credentials:

```bash
cat ~/.krakenapi
```

Expected format:
```
KRAKEN_API_KEY=your_api_key_here
KRAKEN_API_SECRET=your_api_secret_here
```

### Permission Errors

```
Error: EGeneral:Permission denied
```

**Solution**: Ensure your Kraken API key has the required permissions (Funds: Query, Orders: Query/Create/Cancel).

### Insufficient Funds

```
Error: EOrder:Insufficient funds
```

**Solution**: Ensure you have enough USD to buy or enough crypto to sell in your Kraken account.

### Network Errors

```
Error: Connection timeout
```

**Solution**: Check your internet connection. The bot will retry automatically.

### Invalid Trading Pair

```
Error: Invalid trading pair
```

**Solution**: Verify your TRADING_PAIR is correct. Try common formats like `XBTUSD`, `BTCUSD`, `XRPUSD`.

## Customization

You can extend the bot by modifying:

### Adding Indicators

Add technical analysis in `trading_bot.py`:

```python
def should_buy(self, current_price: float) -> bool:
    # Add your custom logic
    if self.rsi_oversold():
        return True
    return current_price <= self.buy_price
```

### Changing Order Types

Modify `kraken_client.py` to use limit orders:

```python
response = self.trade.create_order(
    pair=pair,
    side="buy",
    type="limit",
    volume=volume,
    price=limit_price
)
```

### Adding Stop Loss

Add stop-loss order placement in `execute_buy()`:

```python
# After successful buy
self.place_stop_loss_order(entry_price, stop_loss_offset)
```

## Support

For issues or questions:
1. Check the log file (`trading_bot.log`)
2. Review Kraken API documentation: https://docs.kraken.com/rest/
3. Verify your API credentials and permissions
4. Ensure your trading pair is valid on Kraken

## License

This project is provided as-is for educational purposes. Use at your own risk.

## Disclaimer

**This software is for educational purposes only. The authors are not responsible for any financial losses incurred while using this trading bot. Cryptocurrency trading involves substantial risk of loss.**
