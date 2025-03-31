"""
Music player module for Discord music bot.
"""
import asyncio
import discord
from discord.ext import commands
from typing import Optional, Callable

from src.music.queue import queue_manager
from src.music.ytdl import YTDLSource

class MusicPlayer:
    """
    Handles music playback functionality for the bot.
    """
    def __init__(self, bot: commands.Bot):
        """
        Initialize the music player.
        
        Args:
            bot (commands.Bot): The Discord bot instance
        """
        self.bot = bot
        self._current_ctx: Optional[commands.Context] = None
    
    @property
    def is_playing(self) -> bool:
        """Check if the bot is currently playing music"""
        if not self._current_ctx or not self._current_ctx.voice_client:
            return False
        return self._current_ctx.voice_client.is_playing()
    
    @property
    def is_paused(self) -> bool:
        """Check if the bot is currently paused"""
        if not self._current_ctx or not self._current_ctx.voice_client:
            return False
        return self._current_ctx.voice_client.is_paused()
    
    async def connect_to_voice(self, ctx: commands.Context) -> Optional[discord.VoiceClient]:
        """
        Connect to the user's voice channel.
        
        Args:
            ctx (commands.Context): Command context
            
        Returns:
            Optional[discord.VoiceClient]: Voice client if successfully connected, None otherwise
        """
        if not ctx.author.voice:
            await ctx.send(f"{ctx.author.name} is not connected to a voice channel")
            return None
        
        voice_channel = ctx.author.voice.channel
        voice_client = ctx.voice_client
        
        if voice_client is None:
            try:
                voice_client = await voice_channel.connect()
                await ctx.send(f"Joined {voice_channel}")
                self._current_ctx = ctx
                return voice_client
            except Exception as e:
                await ctx.send(f"Failed to join {voice_channel}: {e}")
                return None
        elif voice_client.channel != voice_channel:
            await voice_client.move_to(voice_channel)
            await ctx.send(f"Moved to {voice_channel}")
            self._current_ctx = ctx
            return voice_client
        else:
            self._current_ctx = ctx
            return voice_client
    
    async def play_from_url_or_search(self, ctx: commands.Context, query: str) -> None:
        """
        Play music from URL or search query.
        
        Args:
            ctx (commands.Context): Command context
            query (str): URL or search query
        """
        voice_client = await self.connect_to_voice(ctx)
        if not voice_client:
            return
        
        async with ctx.typing():
            try:
                # Check if query is a URL
                if query.startswith(('http://', 'https://')):
                    await self._handle_url(ctx, query)
                else:
                    await self._handle_search(ctx, query)
            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")
    
    async def _handle_url(self, ctx: commands.Context, url: str) -> None:
        """
        Handle playback from a direct URL.
        
        Args:
            ctx (commands.Context): Command context
            url (str): URL to play
        """
        try:
            # Extract info to get the title
            info = await self.bot.loop.run_in_executor(None, lambda: YTDLSource.ytdl.extract_info(url, download=False))
            
            if 'entries' in info:
                # It's a playlist or single video in a playlist format
                title = info['entries'][0]['title']
                url = info['entries'][0]['webpage_url']
            else:
                title = info['title']
                
            # Add to queue
            queue_manager.add(title, url)
            await ctx.send(f'Added to queue: {title}')
            
            # If nothing is playing, start playback
            if not self.is_playing:
                await self._play_next(ctx)
                
        except Exception as e:
            await ctx.send(f'An error occurred: {str(e)}')
    
    async def _handle_search(self, ctx: commands.Context, query: str) -> None:
        """
        Handle search query by adding first result to queue.
        
        Args:
            ctx (commands.Context): Command context
            query (str): Search query
        """
        try:
            # Format query for YouTube search
            search_query = f"ytsearch1:{query}"
            info = await self.bot.loop.run_in_executor(None, lambda: YTDLSource.ytdl.extract_info(search_query, download=False))
            
            if 'entries' in info and info['entries']:
                entry = info['entries'][0]
                title = entry['title']
                url = entry['webpage_url']
                
                # Add to queue
                queue_manager.add(title, url)
                await ctx.send(f'Added to queue: {title}')
                
                # If nothing is playing, start playback
                if not self.is_playing:
                    await self._play_next(ctx)
            else:
                await ctx.send("No search results found.")
                
        except Exception as e:
            await ctx.send(f'An error occurred: {str(e)}')
    
    async def _play_next(self, ctx: commands.Context) -> None:
        """
        Play the next song in the queue.
        
        Args:
            ctx (commands.Context): Command context
        """
        if not ctx.voice_client:
            return
            
        next_item = await queue_manager.get_next()
        if next_item:
            try:
                # Check if next_item includes a timestamp (tuple of 3 elements)
                if len(next_item) == 3:
                    title, url, timestamp = next_item
                    player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True, timestamp=timestamp)
                else:
                    title, url = next_item
                    player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                
                # Define callback for when song ends
                def after_play(error):
                    if error:
                        asyncio.run_coroutine_threadsafe(
                            ctx.send(f'An error occurred: {error}'),
                            self.bot.loop
                        )
                    asyncio.run_coroutine_threadsafe(self._play_next(ctx), self.bot.loop)
                
                ctx.voice_client.play(player, after=after_play)
                await ctx.send(f'Now playing: {player.title}')
                
            except Exception as e:
                await ctx.send(f'An error occurred while playing ({title}): {str(e)}')
                await self._play_next(ctx)
        else:
            await ctx.send("Queue is empty. Disconnecting...")
            await ctx.voice_client.disconnect()
    
    async def pause(self, ctx: commands.Context) -> None:
        """
        Pause the currently playing song.
        
        Args:
            ctx (commands.Context): Command context
        """
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("The song has been paused.")
        else:
            await ctx.send("The bot is not playing anything at the moment.")
    
    async def resume(self, ctx: commands.Context) -> None:
        """
        Resume the paused song.
        
        Args:
            ctx (commands.Context): Command context
        """
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("The song has been resumed.")
        else:
            await ctx.send("The bot was not playing anything before this. Use play command.")
    
    async def skip(self, ctx: commands.Context) -> None:
        """
        Skip the currently playing song.
        
        Args:
            ctx (commands.Context): Command context
        """
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Skipped the current song.")
        else:
            await ctx.send("The bot is not playing anything at the moment.")
    
    async def timestamp_skip(self, ctx: commands.Context, timestamp: str) -> None:
        """
        Skip to a specific timestamp in the current song.
        
        Args:
            ctx (commands.Context): Command context
            timestamp (str): Timestamp in mm:ss format
        """
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await ctx.send("The bot is not playing anything at the moment.")
            return
            
        try:
            # Parse the timestamp
            minutes, seconds = map(int, timestamp.split(':'))
            if minutes < 0 or seconds < 0 or seconds >= 60:
                await ctx.send("Invalid timestamp format. Use mm:ss or m:ss.")
                return
            
            total_seconds = minutes * 60 + seconds
            
            # Get current song
            current_song = queue_manager.current
            if not current_song:
                await ctx.send("No current song found in queue.")
                return
                
            title, url = current_song
            
            # Add the timestamped version of the current song to the front of the queue
            # We need to do this before removing the current song from the queue
            queue_manager.add_to_front(f"{title} (from {timestamp})", url, timestamp=total_seconds)
            
            # Now skip the current song - this will trigger the normal after_play callback
            # which will play the next song in the queue (our timestamped version)
            ctx.voice_client.stop()
            await ctx.send(f"Skipping to {timestamp} in {title}...")
            
        except ValueError:
            await ctx.send("Invalid timestamp format. Use mm:ss or m:ss.")
    
    async def leave(self, ctx: commands.Context) -> None:
        """
        Disconnect from voice channel and clear queue.
        
        Args:
            ctx (commands.Context): Command context
        """
        voice_client = ctx.voice_client
        if voice_client:
            voice_client.stop()
            await voice_client.disconnect()
            queue_manager.clear()
            await ctx.send("The bot has left the voice channel.")
        else:
            await ctx.send("The bot is not connected to a voice channel.")

# Singleton instance
player = None

def get_player(bot: commands.Bot) -> MusicPlayer:
    """
    Get the music player singleton instance.
    
    Args:
        bot (commands.Bot): The Discord bot instance
        
    Returns:
        MusicPlayer: The music player instance
    """
    global player
    if player is None:
        player = MusicPlayer(bot)
    return player 