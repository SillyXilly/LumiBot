# Automated YouTube Cookie Refresh Setup

## Overview
This system automatically refreshes YouTube cookies daily to prevent authentication issues with your Discord music bot. No more manual cookie management!

## What's Included

### 🤖 **Automated Scripts**
- `scripts/refresh_cookies.py` - Main cookie refresh script
- `scripts/setup_automation.sh` - One-time setup script
- `scripts/install_cron.sh` - Cron job installer
- `scripts/requirements_automation.txt` - Additional Python dependencies

### 📋 **Configuration Files**
- `env_template.txt` - Environment variables template
- `AUTOMATION_SETUP.md` - This documentation

## Quick Setup Guide

### Step 1: Update Environment Variables
Add these to your `.env` file:
```bash
# YouTube Authentication (for automated cookie refresh)
YOUTUBE_EMAIL=your_youtube_email@gmail.com
YOUTUBE_PASSWORD=your_youtube_password
```

### Step 2: Run Setup Script
SSH into your server and run:
```bash
cd ~/apps/LumiBot
chmod +x scripts/setup_automation.sh
./scripts/setup_automation.sh
```

This will:
- ✅ Install Google Chrome
- ✅ Install ChromeDriver
- ✅ Install Python dependencies (selenium)
- ✅ Make scripts executable

### Step 3: Test Cookie Refresh
```bash
python scripts/refresh_cookies.py
```

You should see output like:
```
🚀 Starting YouTube cookie refresh...
✅ Chrome driver initialized successfully
🔐 Logging into YouTube...
✅ Successfully logged into YouTube
🍪 Extracting cookies...
✅ Successfully extracted 15 cookies to cookies.txt
🔍 Validating cookies...
✅ Cookies validated successfully
🎉 Cookie refresh completed successfully!
```

### Step 4: Install Cron Job
```bash
chmod +x scripts/install_cron.sh
./scripts/install_cron.sh
```

This sets up daily automatic cookie refresh at 6:00 AM.

## How It Works

### 🔄 **Automated Process**
1. **Headless Chrome** launches invisibly
2. **Logs into Google/YouTube** using your credentials
3. **Extracts fresh cookies** from the browser session
4. **Saves cookies** in Netscape format for yt-dlp
5. **Validates cookies** by testing with yt-dlp
6. **Logs results** for monitoring

### ⏰ **Daily Schedule**
- **Time**: 6:00 AM daily
- **Log Location**: `~/apps/LumiBot/logs/cookie_refresh.log`
- **Automatic**: No manual intervention needed

## Monitoring & Troubleshooting

### Check Cron Job Status
```bash
crontab -l  # View installed cron jobs
```

### Monitor Logs
```bash
tail -f ~/apps/LumiBot/logs/cookie_refresh.log
```

### Manual Cookie Refresh
```bash
cd ~/apps/LumiBot
python scripts/refresh_cookies.py
```

### Common Issues

#### ❌ "Chrome driver not found"
**Solution**: Run the setup script again:
```bash
./scripts/setup_automation.sh
```

#### ❌ "Login failed"
**Solutions**:
1. Check your credentials in `.env`
2. Enable 2-factor authentication and use app password
3. Check if Google blocked the login attempt

#### ❌ "Cookies validation failed"
**Solutions**:
1. Try running the script manually
2. Check if YouTube changed their authentication
3. Verify yt-dlp is installed and updated

## Security Considerations

### 🔒 **Credential Security**
- Store credentials in `.env` file (not in code)
- Use app-specific passwords if 2FA is enabled
- Limit server access to trusted users

### 🛡️ **Browser Security**
- Headless Chrome runs with minimal privileges
- No GUI access or persistent browser data
- Cookies are stored locally and not transmitted

## Advanced Configuration

### Custom Schedule
Edit the cron job for different timing:
```bash
crontab -e
# Change: 0 6 * * * (6 AM daily)
# To:     0 */6 * * * (every 6 hours)
```

### Multiple Accounts
Create separate scripts for different YouTube accounts:
```bash
cp scripts/refresh_cookies.py scripts/refresh_cookies_account2.py
# Edit the new script to use different env variables
```

## Benefits

### ✅ **Fully Automated**
- No manual cookie management
- Runs automatically every day
- Self-healing if cookies expire

### ✅ **Reliable**
- Uses real browser session
- Handles Google's security measures
- Validates cookies before use

### ✅ **Secure**
- Credentials stored securely
- No persistent browser data
- Minimal attack surface

### ✅ **Maintainable**
- Comprehensive logging
- Easy monitoring
- Simple troubleshooting

## Troubleshooting Commands

```bash
# Check if Chrome is installed
google-chrome --version

# Check if ChromeDriver is installed
chromedriver --version

# Test yt-dlp with current cookies
yt-dlp --cookies cookies.txt --get-title "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# View recent log entries
tail -20 logs/cookie_refresh.log

# Test login manually (interactive)
python -c "from scripts.refresh_cookies import YouTubeCookieRefresher; r = YouTubeCookieRefresher(); r.refresh_cookies()"
```

Your Discord music bot will now have fresh YouTube cookies automatically! 🎵✨
