#!/bin/bash
# Update existing cron job to run every 30 minutes instead of daily

echo "🔄 Updating cookie refresh cron job frequency..."

# Check if cron job exists
if crontab -l 2>/dev/null | grep -q "refresh_cookies.py"; then
    echo "📅 Found existing cron job - updating frequency..."
    
    # Remove old cron job and add new one with 30-minute frequency
    NEW_CRON_JOB="*/30 * * * * cd /home/afleel/apps/LumiBot && python scripts/refresh_cookies.py >> logs/cookie_refresh.log 2>&1"
    
    # Update cron job
    (crontab -l 2>/dev/null | grep -v "refresh_cookies.py"; echo "$NEW_CRON_JOB") | crontab -
    
    echo "✅ Cron job updated successfully!"
    echo "📅 New schedule: Every 30 minutes"
    echo ""
    echo "🔍 Current cron jobs:"
    crontab -l | grep "refresh_cookies.py"
else
    echo "❌ No existing cookie refresh cron job found."
    echo "💡 Run ./scripts/install_cron.sh to install the cron job first."
fi

echo ""
echo "📊 To monitor cookie refresh activity:"
echo "   tail -f ~/apps/LumiBot/logs/cookie_refresh.log"
