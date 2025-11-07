# YouTube Cookie Setup Guide

## The Problem
YouTube now requires authentication to prevent bot detection. You're seeing this error:
```
Sign in to confirm you're not a bot. Use --cookies-from-browser or --cookies for the authentication.
```

## Solution Options

### Option 1: Browser Cookie Extraction (Recommended)
The bot is now configured to automatically extract cookies from your Chrome browser.

**Requirements:**
1. You must be logged into YouTube in Chrome
2. Chrome must be installed on the same machine as the bot

**How it works:**
- The bot automatically extracts your YouTube session cookies from Chrome
- No manual cookie file needed
- Automatically stays updated with your browser session

### Option 2: Manual Cookie File (Alternative)
If Option 1 doesn't work, you can manually export cookies.

**Steps:**
1. Install a browser extension like "Get cookies.txt LOCALLY"
2. Go to YouTube.com while logged in
3. Export cookies to a file named `cookies.txt`
4. Place the file in your bot's root directory
5. Update `src/config.py`:
   ```python
   # Replace the cookiesfrombrowser line with:
   'cookiefile': 'cookies.txt',
   ```

### Option 3: Different Browser
If you use Firefox instead of Chrome, update `src/config.py`:
```python
'cookiesfrombrowser': ('firefox',),  # For Firefox
# or
'cookiesfrombrowser': ('edge',),     # For Edge
```

## Supported Browsers
- chrome
- firefox
- safari
- edge
- opera
- brave

## Troubleshooting

### If you get "No cookies found" error:
1. Make sure you're logged into YouTube in your browser
2. Try closing and reopening your browser
3. Clear browser cache and log in again

### If cookies still don't work:
1. Try the manual cookie file method (Option 2)
2. Make sure your YouTube account is in good standing
3. Try using a different browser

### Privacy Note
The bot only reads YouTube authentication cookies and doesn't access any other personal data from your browser.

## Testing
After setup, try the bot again with:
```
!play pokemon song
```

The authentication error should be resolved!
