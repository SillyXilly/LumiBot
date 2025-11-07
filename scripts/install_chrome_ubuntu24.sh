#!/bin/bash
# Chrome installation script for Ubuntu 24.04+ (modern method)

echo "🚀 Installing Chrome on Ubuntu 24.04+..."

# Method 1: Direct .deb download (most reliable)
install_chrome_direct() {
    echo "📥 Method 1: Downloading Chrome .deb package directly..."
    
    # Download Chrome .deb package
    wget -q -O /tmp/google-chrome-stable_current_amd64.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    
    if [ $? -eq 0 ]; then
        echo "✅ Chrome package downloaded successfully"
        
        # Install Chrome
        sudo dpkg -i /tmp/google-chrome-stable_current_amd64.deb
        
        # Fix any dependency issues
        sudo apt-get install -f -y
        
        # Clean up
        rm /tmp/google-chrome-stable_current_amd64.deb
        
        # Test installation
        if command -v google-chrome &> /dev/null; then
            echo "✅ Google Chrome installed successfully!"
            google-chrome --version
            return 0
        else
            echo "❌ Chrome installation failed"
            return 1
        fi
    else
        echo "❌ Failed to download Chrome package"
        return 1
    fi
}

# Method 2: Chromium as fallback (easier to install)
install_chromium_fallback() {
    echo "📥 Method 2: Installing Chromium as fallback..."
    
    sudo apt update
    sudo apt install -y chromium-browser
    
    if command -v chromium-browser &> /dev/null; then
        echo "✅ Chromium installed successfully!"
        chromium-browser --version
        
        # Create symlink so scripts can find it as 'google-chrome'
        sudo ln -sf /usr/bin/chromium-browser /usr/local/bin/google-chrome
        
        return 0
    else
        echo "❌ Chromium installation failed"
        return 1
    fi
}

# Method 3: Snap installation
install_chrome_snap() {
    echo "📥 Method 3: Installing Chrome via Snap..."
    
    if command -v snap &> /dev/null; then
        sudo snap install chromium
        
        if snap list | grep -q chromium; then
            echo "✅ Chromium (snap) installed successfully!"
            
            # Create wrapper script
            sudo tee /usr/local/bin/google-chrome > /dev/null << 'EOF'
#!/bin/bash
exec /snap/bin/chromium "$@"
EOF
            sudo chmod +x /usr/local/bin/google-chrome
            
            return 0
        else
            echo "❌ Snap Chromium installation failed"
            return 1
        fi
    else
        echo "❌ Snap not available"
        return 1
    fi
}

# Try installation methods in order
echo "🔧 Attempting Chrome installation..."

if install_chrome_direct; then
    echo "🎉 Chrome installed via direct download!"
elif install_chromium_fallback; then
    echo "🎉 Chromium installed as Chrome alternative!"
elif install_chrome_snap; then
    echo "🎉 Chromium installed via Snap!"
else
    echo "❌ All installation methods failed"
    echo ""
    echo "🔧 Manual installation options:"
    echo "1. Try: sudo apt install chromium-browser"
    echo "2. Or download Chrome manually from: https://www.google.com/chrome/"
    echo "3. Or use Firefox: sudo apt install firefox"
    exit 1
fi

echo ""
echo "🧪 Testing browser installation..."
if command -v google-chrome &> /dev/null; then
    echo "✅ Browser is accessible as 'google-chrome'"
    google-chrome --version
else
    echo "❌ Browser not accessible as 'google-chrome'"
    echo "🔍 Available browsers:"
    command -v chromium-browser && echo "  - chromium-browser"
    command -v firefox && echo "  - firefox"
fi

echo ""
echo "🎯 Next steps:"
echo "1. Test cookie refresh: python scripts/refresh_cookies.py"
echo "2. If issues persist, check CHROME_TROUBLESHOOTING.md"
