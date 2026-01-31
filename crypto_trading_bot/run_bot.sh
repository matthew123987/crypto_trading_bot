#!/bin/bash
# Script to run the trading bot in the background

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create logs directory if it doesn't exist
mkdir -p logs

echo "=========================================="
echo "Starting XRP Trading Bot in Background"
echo "=========================================="
echo "Log file: $SCRIPT_DIR/trading_bot.log"
echo ""
echo "To view logs: tail -f trading_bot.log"
echo "To stop bot: ./stop_bot.sh"
echo "=========================================="
echo ""

# Run the bot with nohup (keeps running after terminal closes)
nohup python3 trading_bot.py > logs/bot_output.log 2>&1 &
BOT_PID=$!

# Save PID for stopping later
echo $BOT_PID > bot.pid

echo "Bot started with PID: $BOT_PID"
echo ""
echo "Bot is now running in the background."
echo "It will continue running even if you:"
echo "  - Close the terminal"
echo "  - Lock your laptop"
echo "  - Log out"
echo ""
echo "Monitor with: tail -f trading_bot.log"
echo "Stop with: ./stop_bot.sh"
