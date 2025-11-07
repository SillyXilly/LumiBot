#!/bin/bash
# Quick Chrome setup for cookie refresh automation

echo "🚀 Quick Chrome setup for cookie refresh..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run this script as root (without sudo)"
    echo "💡 Run: ./scripts/quick_chrome_setup.sh"
    exit 1
fi

# Update system packages
echo "📦 Updating system packages..."
sudo apt update

# Install Chrome if not already installed
if ! command -v google-chrome &> /dev/null; then
    echo "🌐 Installing Google Chrome..."
    
    # Add Google's signing key
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    
    # Add Chrome repository
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
    
    # Update package list and install Chrome
    sudo apt update
    sudo apt install -y google-chrome-stable
    
    echo "✅ Google Chrome installed successfully"
else
    echo "✅ Google Chrome is already installed"
fi

# Install Python dependencies for automation
echo "🐍 Installing Python dependencies..."
pip install selenium webdriver-manager

# Test Chrome installation
echo "🧪 Testing Chrome installation..."
if google-chrome --version; then
    echo "✅ Chrome is working correctly"
else
    echo "❌ Chrome installation may have issues"
    exit 1
fi

# Test cookie refresh script
echo "🍪 Testing cookie refresh script..."
if [ -f "scripts/refresh_cookies.py" ]; then
    echo "✅ Cookie refresh script found"
    
    # Check if .env file has credentials
    if [ -f ".env" ]; then
        if grep -q "YOUTUBE_EMAIL" .env && grep -q "YOUTUBE_PASSWORD" .env; then
            echo "✅ YouTube credentials found in .env"
            echo ""
            echo "🎯 Ready to test! Run:"
            echo "   python scripts/refresh_cookies.py"
        else
            echo "⚠️ Please add YouTube credentials to your .env file:"
            echo "   YOUTUBE_EMAIL=your_email@gmail.com"
            echo "   YOUTUBE_PASSWORD=your_password"
        fi
    else
        echo "⚠️ Please create a .env file with YouTube credentials:"
        echo "   YOUTUBE_EMAIL=your_email@gmail.com"
        echo "   YOUTUBE_PASSWORD=your_password"
    fi
else
    echo "❌ Cookie refresh script not found"
    echo "💡 Make sure you're in the bot directory: cd ~/apps/LumiBot"
fi

echo ""
echo "🎉 Chrome setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Add YouTube credentials to .env file (if not done)"
echo "2. Test: python scripts/refresh_cookies.py"
echo "3. Install cron job: ./scripts/install_cron.sh"
