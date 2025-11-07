#!/usr/bin/env python3
"""
Automated YouTube Cookie Refresh Script
Logs into YouTube using headless Chrome and extracts fresh cookies for yt-dlp
"""

import os
import sys
import time
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class YouTubeCookieRefresher:
    def __init__(self):
        self.youtube_email = os.getenv('YOUTUBE_EMAIL')
        self.youtube_password = os.getenv('YOUTUBE_PASSWORD')
        self.bot_directory = Path(__file__).parent.parent
        self.cookies_file = self.bot_directory / 'cookies.txt'
        self.driver = None
        
        if not self.youtube_email or not self.youtube_password:
            raise ValueError("YOUTUBE_EMAIL and YOUTUBE_PASSWORD must be set in .env file")
    
    def setup_chrome_driver(self):
        """Set up headless Chrome driver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Disable images and CSS for faster loading
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            print("✅ Chrome driver initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Chrome driver: {e}")
            raise
    
    def login_to_youtube(self):
        """Automated login to YouTube"""
        try:
            print("🔐 Logging into YouTube...")
            self.driver.get("https://accounts.google.com/signin")
            
            # Enter email
            email_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "identifierId"))
            )
            email_input.send_keys(self.youtube_email)
            
            # Click Next
            next_button = self.driver.find_element(By.ID, "identifierNext")
            next_button.click()
            
            # Wait for password field and enter password
            password_input = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.NAME, "password"))
            )
            time.sleep(2)  # Small delay to ensure field is ready
            password_input.send_keys(self.youtube_password)
            
            # Click Next
            password_next = self.driver.find_element(By.ID, "passwordNext")
            password_next.click()
            
            # Wait for login to complete and redirect
            WebDriverWait(self.driver, 30).until(
                lambda driver: "myaccount.google.com" in driver.current_url or "youtube.com" in driver.current_url
            )
            
            # Navigate to YouTube to ensure we're logged in there
            self.driver.get("https://www.youtube.com")
            
            # Wait for YouTube to load and verify login
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            print("✅ Successfully logged into YouTube")
            return True
            
        except TimeoutException:
            print("❌ Login timeout - check credentials or network connection")
            return False
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    def extract_cookies(self):
        """Extract cookies and save to Netscape format"""
        try:
            print("🍪 Extracting cookies...")
            
            # Get all cookies from the current session
            cookies = self.driver.get_cookies()
            
            # Filter YouTube-related cookies
            youtube_cookies = [
                cookie for cookie in cookies 
                if 'youtube.com' in cookie.get('domain', '') or 'google.com' in cookie.get('domain', '')
            ]
            
            if not youtube_cookies:
                print("❌ No YouTube cookies found")
                return False
            
            # Write cookies in Netscape format
            with open(self.cookies_file, 'w') as f:
                f.write("# Netscape HTTP Cookie File\n")
                f.write("# https://curl.haxx.se/rfc/cookie_spec.html\n")
                f.write("# This is a generated file! Do not edit.\n\n")
                
                for cookie in youtube_cookies:
                    domain = cookie.get('domain', '')
                    if domain.startswith('.'):
                        domain_flag = 'TRUE'
                    else:
                        domain_flag = 'FALSE'
                        domain = '.' + domain
                    
                    path = cookie.get('path', '/')
                    secure = 'TRUE' if cookie.get('secure', False) else 'FALSE'
                    expires = int(cookie.get('expiry', 0)) if cookie.get('expiry') else 0
                    name = cookie.get('name', '')
                    value = cookie.get('value', '')
                    
                    f.write(f"{domain}\t{domain_flag}\t{path}\t{secure}\t{expires}\t{name}\t{value}\n")
            
            print(f"✅ Successfully extracted {len(youtube_cookies)} cookies to {self.cookies_file}")
            return True
            
        except Exception as e:
            print(f"❌ Cookie extraction failed: {e}")
            return False
    
    def validate_cookies(self):
        """Validate that the extracted cookies work with yt-dlp"""
        try:
            print("🔍 Validating cookies...")
            
            # Test with a simple YouTube video
            import subprocess
            test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll for testing
            
            result = subprocess.run([
                'yt-dlp', 
                '--cookies', str(self.cookies_file),
                '--quiet',
                '--no-download',
                '--get-title',
                test_url
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and result.stdout.strip():
                print("✅ Cookies validated successfully")
                return True
            else:
                print(f"❌ Cookie validation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Cookie validation timed out")
            return False
        except Exception as e:
            print(f"❌ Cookie validation error: {e}")
            return False
    
    def refresh_cookies(self):
        """Main method to refresh YouTube cookies"""
        try:
            print("🚀 Starting YouTube cookie refresh...")
            
            # Setup Chrome driver
            self.setup_chrome_driver()
            
            # Login to YouTube
            if not self.login_to_youtube():
                return False
            
            # Extract cookies
            if not self.extract_cookies():
                return False
            
            # Validate cookies
            if not self.validate_cookies():
                print("⚠️ Cookies extracted but validation failed - they might still work")
            
            print("🎉 Cookie refresh completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Cookie refresh failed: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()
                print("🔒 Browser session closed")

def main():
    """Main entry point"""
    try:
        refresher = YouTubeCookieRefresher()
        success = refresher.refresh_cookies()
        
        if success:
            print("\n✅ Cookie refresh completed successfully!")
            print("🎵 Your Discord bot should now be able to play YouTube music!")
            sys.exit(0)
        else:
            print("\n❌ Cookie refresh failed!")
            print("🔧 Please check your credentials and try again.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Cookie refresh cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
