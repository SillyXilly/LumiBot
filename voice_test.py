#!/usr/bin/env python3
"""
Simple voice connection test script to diagnose issues.
"""
import asyncio
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create a simple bot for testing
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Voice Test Bot logged in as {bot.user}')
    print(f'Discord.py version: {discord.__version__}')
    print(f'Voice support: {hasattr(discord, "VoiceClient")}')
    try:
        print(f'Opus loaded: {discord.opus.is_loaded()}')
    except Exception as e:
        print(f'Opus check failed: {e}')

@bot.command(name='vtest')
async def voice_test(ctx):
    """Test voice connection"""
    print(f"Voice test command called by {ctx.author}")
    
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel!")
        return
    
    channel = ctx.author.voice.channel
    print(f"Attempting to connect to: {channel}")
    
    try:
        # Try to connect with detailed logging
        print("Starting connection...")
        voice_client = await channel.connect(timeout=15.0, reconnect=True)
        print(f"Successfully connected to {channel}")
        await ctx.send(f"✅ Successfully connected to {channel}")
        
        # Test if we can disconnect
        await asyncio.sleep(2)
        await voice_client.disconnect()
        print("Successfully disconnected")
        await ctx.send("✅ Successfully disconnected")
        
    except asyncio.TimeoutError:
        print("Connection timed out")
        await ctx.send("❌ Connection timed out")
    except Exception as e:
        print(f"Connection failed with error: {e}")
        print(f"Error type: {type(e)}")
        await ctx.send(f"❌ Connection failed: {e}")

@bot.command(name='vstop')
async def stop_test(ctx):
    """Stop the test bot"""
    await ctx.send("Stopping voice test bot...")
    await bot.close()

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("ERROR: DISCORD_TOKEN not found in .env file")
        exit(1)
    
    print("Starting voice connection test...")
    print("Use !vtest in a voice channel to test connection")
    print("Use !vstop to stop the bot")
    
    try:
        bot.run(token)
    except Exception as e:
        print(f"Bot failed to start: {e}")
