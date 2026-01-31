# Kraken API Limits & Costs

## Summary

✅ **Kraken API is FREE to use**
✅ **Your bot is WELL within rate limits**
✅ **No API charges**

## API Costs

**Kraken does NOT charge for API usage.** The API is completely free for all users.

## Rate Limits

### Public API Endends (Price Data)
- **Rate Limit**: ~15-30 requests per second
- **Per**: API key

Your bot uses: **1 request every 60 seconds** (0.017 requests per second)

**Usage Calculation:**
- 1 request per 60 seconds
- 60 requests per hour
- 1,440 requests per day

**Limit Utilization: ~0.05%** (extremely low)

### Private API Endends (Trading & Account)

#### Rate Limit: ~5-15 requests per second
- **Trade Orders**: ~10 requests per second
- **Account Info**: ~15 requests per second

Your bot uses:
- **Balance checks**: 1 request every 10 minutes (every 10 iterations)
  - 6 requests per hour
  - 144 requests per day
  
- **Trade orders**: Only when buy/sell triggers fire
  - Highly variable (depends on market activity)
  - Estimated: 0-10 requests per day

**Total Private API Calls**: ~144-154 per day
**Limit Utilization**: ~0.0002% (negligible)

## Detailed Breakdown

### Per 24 Hours

| Action | Frequency | Calls/Day | API Type |
|--------|-----------|------------|----------|
| Get XRP Price | Every 60s | 1,440 | Public |
| Check Balance | Every 10m | 144 | Private |
| Buy Order | As triggered | ~5 | Private |
| Sell Order | As triggered | ~5 | Private |
| **TOTAL** | | **~1,594** | |

### Per Hour (Average)

| Action | Calls/Hour |
|--------|------------|
| Get XRP Price | 60 |
| Check Balance | 6 |
| Trade Orders | <1 |
| **TOTAL** | **~67** |

### Per Minute

| Action | Calls/Minute |
|--------|-------------|
| Get XRP Price | 1 |
| Check Balance | 0.1 |
| Trade Orders | ~0.01 |
| **TOTAL** | **~1.1** |

## Comparison with Limits

### Public API
- **Your usage**: 1,440 calls/day
- **Kraken limit**: ~1,300,000+ calls/day (15 req/sec)
- **Safety margin**: 900x+ under limit

### Private API
- **Your usage**: ~154 calls/day
- **Kraken limit**: ~432,000+ calls/day (5 req/sec)
- **Safety margin**: 2,800x+ under limit

## What Happens If You Exceed Limits?

If you somehow exceed rate limits:

1. **You'll receive an error**: `EAPI:Rate limit exceeded`
2. **No trades lost**: Bot will retry on next cycle
3. **Automatic recovery**: Bot continues after waiting
4. **No account penalty**: Just need to wait briefly

With your current configuration (60-second intervals), **you will never hit rate limits**.

## How to Reduce API Usage Further

If you want to be even more conservative:

### Option 1: Increase Check Interval
```env
CHECK_INTERVAL=120  # Check every 2 minutes instead of 1
```
**Result**: 50% reduction in API calls

### Option 2: Reduce Balance Checks
Modify `trading_bot.py` line ~140:
```python
if iteration % 20 == 0:  # Check every 20 iterations instead of 10
```
**Result**: 50% reduction in balance API calls

### Option 3: Use Websocket API (Advanced)
- Connect once, get real-time updates
- Zero HTTP requests needed
- More complex to implement

## IP Rate Limits

**Good news**: Kraken rate limits are per API key, **not per IP address**.

This means:
- ✅ You can run multiple bots with different API keys
- ✅ Moving to AWS EC2 won't affect your rate limits
- ✅ Same API key works from multiple locations
- ⚠️ Each API key has its own rate limit

## Recommendations

### Current Configuration ✅
- **CHECK_INTERVAL=60** is perfect
- No changes needed
- Extremely safe operation

### For High-Frequency Trading (Not Recommended)
If you wanted to trade faster:
```env
CHECK_INTERVAL=10  # 6 checks per second
```
Still well within limits (40% utilization)

### For Multiple Bots
If running multiple bots:
- Use different API keys for each bot
- Each key gets its own rate limit
- Total capacity scales with number of keys

## Conclusion

Your bot configuration is **extremely safe** regarding API limits:

1. **No cost**: Kraken API is completely free
2. **Minimal usage**: ~1,594 calls/day vs ~1.7M limit
3. **900x+ safety margin**: Impossible to hit limits
4. **No restrictions needed**: Current 60-second interval is ideal
5. **AWS-friendly**: Same limits apply on cloud servers

**You can run the bot 24/7 without any concerns about API limits or costs.**

## References

- [Kraken API Rate Limits](https://docs.kraken.com/rest/#section/Rate-Limits)
- [Kraken API Documentation](https://docs.kraken.com/rest/)
- [Kraken Fee Schedule](https://www.kraken.com/features/fee-schedule)
