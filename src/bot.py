"""
Main Discord bot module.
"""
import discord
from discord.ext import commands

from src.config import COMMAND_PREFIX, DISCORD_TOKEN
from src.commands.music_commands import setup_music_commands

def create_bot() -> commands.Bot:
    """
    Create and configure the Discord bot.
    
    Returns:
        commands.Bot: The configured bot instance
    """
    # Set up intents
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    
    # Create bot instance
    bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)
    
    # Register event handlers
    @bot.event
    async def on_ready():
        """Called when the bot is ready"""
        print(f"Logged in as {bot.user.name}")
        print(f"Bot ID: {bot.user.id}")
        print("------")
        
        # Set activity status
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening, 
                name=f"{COMMAND_PREFIX}play | {COMMAND_PREFIX}help"
            )
        )
    
    # Register commands
    setup_music_commands(bot)
    
    return bot

def run_bot() -> None:
    """Run the Discord bot"""
    bot = create_bot()
    
    if not DISCORD_TOKEN:
        raise ValueError("No Discord token found in environment variables. "
                        "Please set the DISCORD_TOKEN environment variable.")
    
    bot.run(DISCORD_TOKEN) 