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
        self.is_playing = False
        self.current = None
        self.voice_client = None
        self.disconnect_timer = None
    
    @property
    def is_paused(self) -> bool:
        """Check if the bot is currently paused"""
        if not self._current_ctx or not self._current_ctx.voice_client:
            return False
        return self._current_ctx.voice_client.is_paused()
    
    async def connect_to_voice(self, ctx: commands.Context, retries: int = 3) -> Optional[discord.VoiceClient]:
        """
        Connect to the user's voice channel with retry logic.
        
        Args:
            ctx (commands.Context): Command context
            retries (int): Number of connection attempts
            
        Returns:
            Optional[discord.VoiceClient]: Voice client if successfully connected, None otherwise
        """
        if not ctx.author.voice:
            await ctx.send(f"{ctx.author.name} is not connected to a voice channel")
            return None
        
        voice_channel = ctx.author.voice.channel
        voice_client = ctx.voice_client
        
        # If already connected to the same channel, return existing client
        if voice_client and voice_client.channel == voice_channel and voice_client.is_connected():
            self._current_ctx = ctx
            self.voice_client = voice_client
            return voice_client
        
        # If connected to different channel, disconnect first
        if voice_client and voice_client.is_connected():
            try:
                await voice_client.disconnect(force=True)
                await asyncio.sleep(1)  # Wait a moment before reconnecting
            except Exception:
                pass  # Ignore errors when disconnecting
        
        # Attempt to connect with retries
        for attempt in range(retries):
            try:
                voice_client = await voice_channel.connect(timeout=10.0, reconnect=True)
                await ctx.send(f"Joined {voice_channel}")
                self._current_ctx = ctx
                self.voice_client = voice_client
                return voice_client
            except Exception as e:
                if attempt < retries - 1:
                    await ctx.send(f"Connection attempt {attempt + 1} failed, retrying... ({e})")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    await ctx.send(f"Failed to join {voice_channel} after {retries} attempts: {e}")
                    return None
        
        return None
    
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
            def extract_info():
                return YTDLSource.ytdl.extract_info(url, download=False)
            info = await self.bot.loop.run_in_executor(None, extract_info)
            
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
            def extract_search_info():
                return YTDLSource.ytdl.extract_info(search_query, download=False)
            info = await self.bot.loop.run_in_executor(None, extract_search_info)
            
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
        if self.disconnect_timer:
            self.disconnect_timer.cancel()
            self.disconnect_timer = None
            
        if queue_manager.is_empty:
            self.is_playing = False
            self.current = None
            
            # Start disconnect timer
            self.disconnect_timer = asyncio.create_task(self._disconnect_after_delay(ctx))
            return
            
        self.is_playing = True
        self.current = await queue_manager.get_next()
        
        try:
            # Check if next_item includes a timestamp (tuple of 3 elements)
            if len(self.current) == 3:
                title, url, timestamp = self.current
                player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True, timestamp=timestamp)
            else:
                title, url = self.current
                player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            
            # Check if voice client is still connected
            if not self.voice_client or not self.voice_client.is_connected():
                await ctx.send("Voice connection lost. Please try rejoining the voice channel.")
                self.is_playing = False
                return
            
            # Define callback for when song ends
            def after_play(error, **kwargs):
                if error:
                    # Log the error for debugging but don't spam the chat
                    print(f"Playback error: {error}")
                    # Only send message for non-connection errors
                    if "Connection" not in str(error) and "WebSocket" not in str(error):
                        asyncio.run_coroutine_threadsafe(
                            ctx.send(f'An error occurred: {error}'),
                            self.bot.loop
                        )
                asyncio.run_coroutine_threadsafe(self._play_next(ctx), self.bot.loop)
            
            self.voice_client.play(player, after=after_play)
            await ctx.send(f'Now playing: {player.title}')
            
        except Exception as e:
            await ctx.send(f'An error occurred while playing ({title}): {str(e)}')
            await self._play_next(ctx)
    
    async def _disconnect_after_delay(self, ctx: commands.Context) -> None:
        """
        Disconnect from voice channel after 2 minutes if no new songs are added.
        
        Args:
            ctx (commands.Context): Command context
        """
        try:
            await asyncio.sleep(120)  # Wait for 2 minutes
            
            # Check if queue is still empty and we're not playing anything
            if queue_manager.is_empty and not self.is_playing:
                if self.voice_client and self.voice_client.is_connected():
                    try:
                        await self.voice_client.disconnect(force=True)
                        self.voice_client = None
                        await ctx.send("Disconnected due to inactivity.")
                    except Exception as e:
                        # If disconnect fails, just clean up our references
                        self.voice_client = None
                        print(f"Error during auto-disconnect: {e}")
                    
        except asyncio.CancelledError:
            # Timer was cancelled, do nothing
            pass
    
    async def pause(self, ctx: commands.Context) -> None:
        """
        Pause the currently playing song.
        
        Args:
            ctx (commands.Context): Command context
        """
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.pause()
            await ctx.send("The song has been paused.")
        else:
            await ctx.send("The bot is not playing anything at the moment.")
    
    async def resume(self, ctx: commands.Context) -> None:
        """
        Resume the paused song.
        
        Args:
            ctx (commands.Context): Command context
        """
        if self.voice_client and self.voice_client.is_paused():
            self.voice_client.resume()
            await ctx.send("The song has been resumed.")
        else:
            await ctx.send("The bot was not playing anything before this. Use play command.")
    
    async def skip(self, ctx: commands.Context) -> None:
        """
        Skip the currently playing song.
        
        Args:
            ctx (commands.Context): Command context
        """
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()
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
        if not self.voice_client or not self.voice_client.is_playing():
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
            current_song = self.current
            if not current_song:
                await ctx.send("No current song found in queue.")
                return
                
            title, url = current_song
            
            # Add the timestamped version of the current song to the front of the queue
            # We need to do this before removing the current song from the queue
            queue_manager.add_to_front(f"{title} (from {timestamp})", url, timestamp=total_seconds)
            
            # Now skip the current song - this will trigger the normal after_play callback
            # which will play the next song in the queue (our timestamped version)
            self.voice_client.stop()
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
            try:
                if voice_client.is_playing():
                    voice_client.stop()
                await voice_client.disconnect(force=True)
                queue_manager.clear()
                self.is_playing = False
                self.current = None
                self.voice_client = None
                if self.disconnect_timer:
                    self.disconnect_timer.cancel()
                    self.disconnect_timer = None
                await ctx.send("The bot has left the voice channel.")
            except Exception as e:
                await ctx.send(f"Error while leaving voice channel: {e}")
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