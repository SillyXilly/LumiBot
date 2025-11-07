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
    
    # Modern method for Ubuntu 24.04+ (using signed-by)
    echo "📥 Downloading Chrome directly from Google..."
    
    # Download Chrome .deb package directly
    wget -q -O /tmp/google-chrome-stable_current_amd64.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    
    # Install Chrome package
    sudo dpkg -i /tmp/google-chrome-stable_current_amd64.deb
    
    # Fix any dependency issues
    sudo apt-get install -f -y
    
    # Clean up
    rm /tmp/google-chrome-stable_current_amd64.deb
    
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
