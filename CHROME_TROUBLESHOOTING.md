# Chrome & ChromeDriver Troubleshooting Guide

## The Error You're Seeing
```
❌ Failed to initialize Chrome driver: Message: Unable to obtain driver for chrome
```

This means ChromeDriver (the tool that controls Chrome) is not properly installed or accessible.

## Quick Fix Solutions

### Option 1: Run Quick Setup Script ⚡ **RECOMMENDED**
```bash
cd ~/apps/LumiBot
chmod +x scripts/quick_chrome_setup.sh
./scripts/quick_chrome_setup.sh
```

This will:
- ✅ Install Google Chrome
- ✅ Install required Python packages
- ✅ Test the installation
- ✅ Guide you through credential setup

### Option 2: Manual Chrome Installation
```bash
# Update packages
sudo apt update

# Install Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable

# Install Python dependencies
pip install selenium webdriver-manager

# Test Chrome
google-chrome --version
```

### Option 3: Alternative Browser (Firefox)
If Chrome continues to have issues, you can modify the script to use Firefox:

```bash
# Install Firefox
sudo apt install -y firefox

# Install Firefox driver
pip install selenium webdriver-manager

# Modify the script (contact for help with this)
```

## Common Issues & Solutions

### Issue 1: "Chrome not found"
**Solution**: Install Chrome using Option 1 or 2 above.

### Issue 2: "Permission denied"
**Solution**: 
```bash
# Make sure you're not running as root
whoami  # Should NOT show 'root'

# If you are root, switch to your user account
su - afleel
cd ~/apps/LumiBot
```

### Issue 3: "ChromeDriver version mismatch"
**Solution**: The updated script now uses `webdriver-manager` which automatically handles version matching.

### Issue 4: "Display not found" (headless issues)
**Solution**: The script is already configured for headless mode, but if issues persist:
```bash
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &
```

### Issue 5: "Network/Download issues"
**Solution**: 
```bash
# Check internet connectivity
ping google.com

# Try with different mirror
sudo apt update --fix-missing
```

## Verification Steps

### 1. Check Chrome Installation
```bash
google-chrome --version
# Should show: Google Chrome 120.x.x.x
```

### 2. Check Python Dependencies
```bash
pip list | grep selenium
pip list | grep webdriver-manager
# Both should be listed
```

### 3. Test Cookie Refresh
```bash
cd ~/apps/LumiBot
python scripts/refresh_cookies.py
# Should show Chrome driver setup messages
```

### 4. Check .env File
```bash
cat .env | grep YOUTUBE
# Should show your email and password
```

## Environment Setup

### Required .env Variables
```bash
# Add these to your .env file:
YOUTUBE_EMAIL=your_email@gmail.com
YOUTUBE_PASSWORD=your_password

# For Gmail accounts with 2FA, use App Password instead of regular password
```

### App Password Setup (if using 2FA)
1. Go to Google Account settings
2. Security → 2-Step Verification → App passwords
3. Generate app password for "Mail"
4. Use this password in .env instead of your regular password

## Testing the Fix

### Step-by-Step Test
```bash
# 1. Navigate to bot directory
cd ~/apps/LumiBot

# 2. Check Chrome
google-chrome --version

# 3. Test cookie refresh
python scripts/refresh_cookies.py

# 4. Expected output:
# 🚀 Starting YouTube cookie refresh...
# 🔍 Setting up Chrome driver...
# ✅ Chrome driver initialized successfully
# 🔐 Logging into YouTube...
# ✅ Successfully logged into YouTube
# 🍪 Extracting cookies...
# ✅ Successfully extracted X cookies to cookies.txt
```

## Still Having Issues?

### Debug Information to Collect
```bash
# System info
uname -a
lsb_release -a

# Chrome info
google-chrome --version
which google-chrome

# Python info
python --version
pip list | grep selenium

# Permissions
ls -la scripts/refresh_cookies.py
whoami
```

### Alternative: Use Manual Cookies
If automation continues to fail, you can still use manual cookie export:
1. Export cookies from your browser using an extension
2. Save as `cookies.txt` in the bot directory
3. The bot will work with manual cookies (just need to refresh them periodically)

The automated system is a convenience feature - your bot will work fine with manual cookies too! 🍪
