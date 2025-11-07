#!/bin/bash
# Setup script for automated YouTube cookie refresh

echo "🚀 Setting up automated YouTube cookie refresh..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update

# Install Chrome
echo "🌐 Installing Google Chrome..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable

# Install ChromeDriver
echo "🚗 Installing ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | cut -d ' ' -f3 | cut -d '.' -f1)
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
sudo unzip /tmp/chromedriver.zip -d /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm /tmp/chromedriver.zip

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install -r scripts/requirements_automation.txt

# Make scripts executable
chmod +x scripts/refresh_cookies.py

echo "✅ Setup completed!"
echo ""
echo "📝 Next steps:"
echo "1. Update your .env file with YouTube credentials:"
echo "   YOUTUBE_EMAIL=your_email@gmail.com"
echo "   YOUTUBE_PASSWORD=your_password"
echo ""
echo "2. Test the cookie refresh script:"
echo "   python scripts/refresh_cookies.py"
echo ""
echo "3. Set up the cron job for automatic refresh:"
echo "   crontab -e"
echo "   Add: 0 6 * * * cd /home/afleel/apps/LumiBot && python scripts/refresh_cookies.py >> logs/cookie_refresh.log 2>&1"
