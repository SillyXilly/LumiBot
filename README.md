# Discord Music Bot

A simple Discord music bot to play music in voice channels from YouTube URLs, search terms, or playlists.

## Features

- Play music from YouTube URLs
- Search for songs by name
- Play YouTube playlists
- Queue management (add, list, skip, clear, shuffle)
- Timestamp navigation
- Voice channel control

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Make sure you have [FFmpeg](https://ffmpeg.org/download.html) installed on your system
4. Create a `.env` file with your Discord bot token and YouTube credentials:
   ```
   DISCORD_TOKEN=your_discord_bot_token_here
   ```

## Usage

Run the bot:
```
python main.py
```

## Commands

The bot uses `!` as the default command prefix.

### Music Control
- `!play <url or search term>` - Play a song from URL or search
- `!search <search term>` - Show top 5 search results and choose
- `!playlist <url>` - Add a YouTube playlist to the queue
- `!skip` - Skip the current song
- `!tskip <mm:ss>` - Skip to a specific timestamp in the song
- `!pause` - Pause the current song
- `!resume` - Resume playback

### Queue Management
- `!qlist` - Show the current queue
- `!qskip <number>` - Skip to a specific song in the queue
- `!qclear` - Clear the entire queue
- `!shuffle` - Shuffle the remaining songs in the queue

### Channel Control
- `!leave` - Make the bot leave the voice channel

**Important security notes:**
- Don't share or commit your .env file
- This setup is for personal use only

## Requirements

- Python 3.8+
- discord.py
- yt-dlp
- FFmpeg

## License

MIT 