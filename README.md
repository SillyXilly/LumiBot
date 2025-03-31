# LumiBot

A Discord music bot with advanced features including YouTube playback, playlist management, and game-related commands.

## Features

### Music Commands
- `!play <song>` - Play a song from YouTube
- `!pause` - Pause the current song
- `!resume` - Resume the paused song
- `!skip` - Skip the current song
- `!tskip <timestamp>` - Skip to a specific timestamp in the current song (e.g., `!tskip 2:30`)
- `!qlist` - Display the current queue
- `!qclear` - Clear the queue
- `!leave` - Disconnect the bot from the voice channel
- `!shuffle` - Shuffle the current queue
- `!search <query>` - Search for a song and choose from results
- `!playlist <url>` - Play all songs from a YouTube playlist
- `!qskip <index>` - Skip to a specific song in the queue

### Game Commands
- `!team <players>` - Randomly assign players to League of Legends lanes (2-5 players)
- `!assign <players>` - Randomly assign players to League of Legends lanes and suggest champions (2-5 players)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/SillyXilly/LumiBot.git
cd LumiBot
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your Discord bot token:
```
DISCORD_TOKEN=your_bot_token_here
COMMAND_PREFIX=!
```

5. Run the bot:
```bash
python main.py
```

## Requirements
- Python 3.8 or higher
- FFmpeg installed on your system
- Discord.py
- yt-dlp
- python-dotenv

## Contributing
Feel free to submit issues and enhancement requests!

## License
This project is licensed under the MIT License - see the LICENSE file for details. 