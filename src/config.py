"""
Configuration module for the Discord music bot.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# YouTube downloader configuration
YTDL_FORMAT_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

# FFmpeg configuration
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

# Search configuration
MAX_SEARCH_RESULTS = 5
PLAYLIST_LIMIT = 30

# Data Dragon API configuration
DATA_DRAGON_BASE_URL = "https://ddragon.leagueoflegends.com"
DATA_DRAGON_VERSION = "15.6.1"  # Latest version as of now
DATA_DRAGON_CHAMPION_URL = f"{DATA_DRAGON_BASE_URL}/cdn/{DATA_DRAGON_VERSION}/data/en_US/champion.json" 