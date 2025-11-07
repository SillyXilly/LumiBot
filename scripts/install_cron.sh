#!/bin/bash
# Install cron job for automated cookie refresh

echo "⏰ Setting up automated cookie refresh cron job..."

# Create logs directory if it doesn't exist
mkdir -p ~/apps/LumiBot/logs

# Create the cron job entry
CRON_JOB="0 6 * * * cd /home/afleel/apps/LumiBot && python scripts/refresh_cookies.py >> logs/cookie_refresh.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "refresh_cookies.py"; then
    echo "⚠️ Cron job already exists. Updating..."
    # Remove existing job and add new one
    (crontab -l 2>/dev/null | grep -v "refresh_cookies.py"; echo "$CRON_JOB") | crontab -
else
    echo "➕ Adding new cron job..."
    # Add new job to existing crontab
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
fi

echo "✅ Cron job installed successfully!"
echo ""
echo "📅 Schedule: Daily at 6:00 AM"
echo "📝 Logs: ~/apps/LumiBot/logs/cookie_refresh.log"
echo ""
echo "🔍 To view current cron jobs:"
echo "   crontab -l"
echo ""
echo "📊 To monitor the log:"
echo "   tail -f ~/apps/LumiBot/logs/cookie_refresh.log"
