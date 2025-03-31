# LumiBot

A Discord bot with music playback capabilities and game-related features.

## Features

### Music Features
- Play music from YouTube URLs or search queries
- Queue management system
- Skip, pause, and resume playback
- Timestamp skipping within songs
- Volume control
- Disconnect from voice channel

### Game Features
- League of Legends team assignment
  - Randomly assign 2-5 players to different lanes
  - Supports all standard lanes (Top, Jungle, Mid, Bot, Support)
  - Clean embed presentation of assignments

## Commands

### Music Commands
- `!play <url or search query>` - Play music from a URL or search query
- `!skip` - Skip the current song
- `!pause` - Pause the current song
- `!resume` - Resume the paused song
- `!tskip <timestamp>` - Skip to a specific timestamp in the current song (format: mm:ss)
- `!leave` - Disconnect from the voice channel

### Game Commands
- `!team <player1>,<player2>,...` - Randomly assign 2-5 players to League of Legends lanes

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - `DISCORD_TOKEN`: Your Discord bot token
   - `COMMAND_PREFIX`: Command prefix (default: '!')

4. Run the bot:
   ```bash
   python main.py
   ```

## Requirements
- Python 3.8+
- discord.py
- yt-dlp
- FFmpeg (for audio playback)

## License
MIT License 