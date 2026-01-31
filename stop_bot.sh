#!/bin/bash
# Script to stop the trading bot

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if systemd is managing the bot
if systemctl is-active --quiet crypto-trading-bot.service 2>/dev/null; then
    echo "⚠️  WARNING: Bot is running via systemd service!"
    echo ""
    echo "The bot is managed by systemd. Please use systemctl commands instead:"
    echo ""
    echo "  Stop:    sudo systemctl stop crypto-trading-bot-inhibitor.service crypto-trading-bot.service"
    echo "  Start:   sudo systemctl start crypto-trading-bot-inhibitor.service crypto-trading-bot.service"
    echo "  Status:  sudo systemctl status crypto-trading-bot-inhibitor.service crypto-trading-bot.service"
    echo "  Restart: sudo systemctl restart crypto-trading-bot-inhibitor.service crypto-trading-bot.service"
    echo ""
    echo "Systemd will automatically restart the bot if you kill the process."
    echo "To disable systemd management, run: sudo systemctl disable crypto-trading-bot-inhibitor.service crypto-trading-bot.service"
    echo ""
    exit 1
fi

# Find all trading_bot.py processes
BOT_PIDS=$(ps aux | grep "python3.*trading_bot.py" | grep -v grep | awk '{print $2}')

if [ -z "$BOT_PIDS" ]; then
    echo "No trading bot processes found running."
    # Clean up bot.pid file if it exists
    [ -f bot.pid ] && rm bot.pid
    exit 0
fi

echo "Stopping XRP Trading Bot..."
echo "Found PIDs: $BOT_PIDS"

# Kill all bot processes
for PID in $BOT_PIDS; do
    echo "Stopping PID: $PID"
    kill $PID 2>/dev/null
done

# Wait for graceful shutdown
sleep 2

# Check if any processes still running and force kill if needed
BOT_PIDS=$(ps aux | grep "python3.*trading_bot.py" | grep -v grep | awk '{print $2}')
if [ -n "$BOT_PIDS" ]; then
    echo "Some processes did not stop gracefully. Force killing..."
    for PID in $BOT_PIDS; do
        echo "Force killing PID: $PID"
        kill -9 $PID 2>/dev/null
    done
    sleep 1
fi

# Clean up bot.pid file
rm -f bot.pid

echo "Bot stopped successfully."
echo ""
echo "Check the final logs: tail -50 trading_bot.log"
