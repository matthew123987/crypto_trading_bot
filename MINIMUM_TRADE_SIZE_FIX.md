# Fix for "volume minimum not met" Error

## Problem

The trading bot was encountering the following error when attempting to sell small amounts of cryptocurrency:

```
ERROR - Error placing limit sell order: The request payload is malformed, incorrect or ambiguous.
Details: {'error': ['EGeneral:Invalid arguments:volume minimum not met']}
```

This occurred because:
1. The bot had a very small amount of BTC (0.00000001 BTC) in the account
2. With `SELL_ALL=True`, it attempted to sell this entire amount
3. Kraken rejected the order because the volume was below their minimum trade size requirement

## Solution

Added a minimum trade size check before placing sell orders to prevent Kraken from rejecting orders due to insufficient volume.

### Changes Made

#### 1. Configuration (`config.py`)
Added a new configuration parameter:
```python
MIN_CRYPTO_TRADE_SIZE: float = float(os.getenv("MIN_CRYPTO_TRADE_SIZE", "0.00001"))
```

Default value: **0.00001 BTC** (adjustable via environment variable)

#### 2. Trading Bot (`trading_bot.py`)
Enhanced `place_sell_limit_order()` method to check minimum trade size:
```python
# Check if amount meets minimum trade size requirement
if crypto_amount < Config.MIN_CRYPTO_TRADE_SIZE:
    logger.warning("⚠ Cannot place sell order: amount ({:.8f} {}) is below minimum trade size ({:.8f} {})".format(
        crypto_amount, self.base_asset, Config.MIN_CRYPTO_TRADE_SIZE, self.base_asset))
    logger.warning("⚠ Skipping sell order - amount too small for Kraken minimum volume requirement")
    return None
```

#### 3. Environment Configuration (`.env.example`)
Added documentation for the new configuration option:
```env
MIN_CRYPTO_TRADE_SIZE=0.00001  # Minimum trade size to avoid "volume minimum not met" errors (in crypto units)
```

## How to Use

### Option 1: Use Default Value
The default minimum trade size of **0.00001** is suitable for most Bitcoin trading scenarios. No changes needed if this works for your use case.

### Option 2: Customize for Your Trading Pair
Different cryptocurrencies may have different minimum trade sizes on Kraken. Adjust the value in your `.env` file:

```env
# For Bitcoin (XBTUSD)
MIN_CRYPTO_TRADE_SIZE=0.00001

# For Ethereum (ETHUSD) - adjust as needed
MIN_CRYPTO_TRADE_SIZE=0.001

# For XRP (XRPUSD) - adjust as needed
MIN_CRYPTO_TRADE_SIZE=10
```

### Finding Minimum Trade Sizes
Refer to Kraken's official documentation for current minimum order sizes:
- [Kraken Minimum Order Size Documentation](https://support.kraken.com/hc/en-us/articles/205893708)

As a general reference:
- **BTC**: ~0.001 BTC (but can be lower for some pairs)
- **ETH**: ~0.01 ETH
- **XRP**: ~50 XRP

*Note: Minimum trade sizes may vary based on the specific trading pair and Kraken's policies.*

## Behavior After Fix

### Before Fix
```
2026-01-03 20:41:16,501 - INFO - Amount: 8.9e-09 BTC
2026-01-03 20:41:16,502 - INFO - Placing limit sell order: 8.9e-09 XBTUSD at $89157.0
2026-01-03 20:41:16,619 - ERROR - Error placing limit sell order: The request payload is malformed, incorrect or ambiguous.
Details: {'error': ['EGeneral:Invalid arguments:volume minimum not met']}
```

### After Fix
```
2026-01-03 20:46:49,353 - INFO - ℹ Cannot place sell order: amount (0.00000001 BTC) is below minimum trade size (0.00001000 BTC)
2026-01-03 20:46:49,353 - INFO - ℹ Skipping sell order - amount too small for Kraken minimum volume requirement
2026-01-03 20:46:49,353 - INFO - Sell order skipped/not placed - checking for available USD to buy...
2026-01-03 20:46:49,353 - INFO - ✓ USD balance: $106.73
2026-01-03 20:46:49,353 - INFO - === PLACING BUY ORDER ===
2026-01-03 20:46:49,353 - INFO - Amount: $100.0
2026-01-03 20:46:49,353 - INFO - Crypto amount: 0.00113301 BTC
2026-01-03 20:46:49,353 - INFO - Limit price: $88265.0
```

**Note**: The "placing sell order" message is now suppressed when the amount is below the minimum trade size, making the logs cleaner and less confusing.

The bot will now:
1. Detect when the sell amount is below the minimum
2. Log an informational message (not a warning, as this is expected behavior)
3. Skip the sell order attempt
4. Check if there's enough USD available to place a buy order
5. If sufficient USD exists, place a buy order to accumulate more crypto
6. Continue running without errors
7. Wait for the next iteration to check again

## Handling Small Balances

If you have a small amount of crypto that cannot be sold due to minimum trade size constraints:

1. **Accumulate**: Wait for more trades to accumulate enough crypto to meet the minimum
2. **Deposit**: Add more crypto to your account to reach the minimum trade size
3. **Adjust Settings**: Increase `DOLLARS_BUY_AMOUNT` to generate larger trade volumes
4. **Manual Trade**: Consider manually trading the small amount outside of the bot

## Troubleshooting

### Issue: "amount too small" warnings keep appearing
**Solution**: Your crypto balance is below the minimum trade size. You can:
- Wait for more buy orders to accumulate crypto
- Increase `DOLLARS_BUY_AMOUNT` in your `.env` file
- Deposit additional crypto to reach the minimum

### Issue: Need to trade smaller amounts than the minimum
**Solution**: Kraken has hard minimums that cannot be bypassed. Consider:
- Trading a different pair with lower minimums
- Using a different exchange with lower minimums
- Increasing your trade amounts

## Backward Compatibility

This fix is fully backward compatible:
- Existing configurations will continue to work
- Default value is applied automatically if not specified
- No breaking changes to existing functionality

## Testing

To verify the fix is working:

1. Check the logs for warning messages about small amounts
2. Confirm no more "volume minimum not met" errors from Kraken
3. Ensure the bot continues running smoothly
4. Verify sell orders are placed when amounts exceed the minimum

Example log output:
```
INFO - ℹ Cannot place sell order: amount (0.00000001 BTC) is below minimum trade size (0.00001000 BTC)
INFO - ℹ Skipping sell order - amount too small for Kraken minimum volume requirement
INFO - Waiting 60 seconds...
```

## Summary

This fix prevents the bot from attempting to place sell orders that Kraken will reject due to minimum volume requirements. The bot now gracefully handles small crypto balances by skipping sell attempts and continuing to run normally until sufficient crypto is accumulated.
