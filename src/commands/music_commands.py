"""
Music commands module for Discord bot.
"""
import asyncio
import validators
import discord
import yt_dlp as youtube_dl
from discord.ext import commands
from typing import Optional

from src.music.player import get_player
from src.music.queue import queue_manager
from src.music.ytdl import YTDLSource
from src.config import PLAYLIST_LIMIT, MAX_SEARCH_RESULTS

def setup_music_commands(bot: commands.Bot) -> None:
    """
    Register all music commands with the bot.
    
    Args:
        bot (commands.Bot): The Discord bot instance
    """
    # Get player instance
    player = get_player(bot)
    
    @bot.command(name='play', help='Play a song from URL or search')
    async def play_command(ctx, *, query):
        """Play a song from URL or search for it"""
        await player.play_from_url_or_search(ctx, query)
    
    @bot.command(name='search', help='Search for a song (shows top 5 results)')
    async def search_command(ctx, *, query):
        """Search for a song and select from results"""
        if not ctx.author.voice:
            await ctx.send(f"{ctx.author.name} is not connected to a voice channel")
            return
            
        voice_client = await player.connect_to_voice(ctx)
        if not voice_client:
            return
            
        async with ctx.typing():
            try:
                # Get search results
                entries, result_message = await YTDLSource.search_source(
                    query, 
                    loop=bot.loop, 
                    max_results=MAX_SEARCH_RESULTS
                )
                
                if not entries:
                    await ctx.send("No search results found.")
                    return
                    
                num_results = len(entries)
                await ctx.send(f"**Top {num_results} search results:**\n{result_message}\n"
                               f"Type the number of the song to play (1-{num_results}) or type 'queue' to add to queue:")
                
                def check(msg):
                    return (msg.author == ctx.author and msg.channel == ctx.channel and 
                            (msg.content.isdigit() and 1 <= int(msg.content) <= num_results) or 
                            msg.content.lower() == 'queue')
                
                try:
                    response = await bot.wait_for('message', check=check, timeout=30)
                    
                    if response.content.lower() == 'queue' or ctx.voice_client.is_playing():
                        # Add first result to queue
                        queue_manager.add(entries[0]['title'], entries[0]['webpage_url'])
                        await ctx.send(f'Song added to queue: {entries[0]["title"]}')
                        
                        if not player.is_playing:
                            await player._play_next(ctx)
                    else:
                        # Play the selected song immediately
                        choice = int(response.content) - 1
                        url = entries[choice]['webpage_url']
                        
                        # Add to queue and play
                        queue_manager.add(entries[choice]['title'], url)
                        
                        if player.is_playing:
                            await ctx.send(f'Added to queue: {entries[choice]["title"]}')
                        else:
                            await player._play_next(ctx)
                
                except asyncio.TimeoutError:
                    await ctx.send("Song selection timed out. Please try again.")
                    
            except Exception as e:
                await ctx.send(f'An error occurred: {str(e)}')
    
    @bot.command(name='playlist', help=f'Play a YouTube playlist (first {PLAYLIST_LIMIT} songs)')
    async def playlist_command(ctx, url: str):
        """Play songs from a YouTube playlist"""
        if not validators.url(url):
            await ctx.send("Please provide a valid URL for the playlist.")
            return
            
        voice_client = await player.connect_to_voice(ctx)
        if not voice_client:
            return
            
        async with ctx.typing():
            try:
                # Create a copy of the ytdl options specifically for playlist handling
                ytdl_options = YTDLSource.ytdl.params.copy()
                ytdl_options.update({
                    'format': 'bestaudio/best',
                    'noplaylist': False,
                    'extract_flat': 'in_playlist',
                    'playlist_items': f'1-{PLAYLIST_LIMIT}'
                })
                
                # Create a temporary ytdl instance with these options
                temp_ytdl = youtube_dl.YoutubeDL(ytdl_options)
                
                def extract_playlist_info():
                    return temp_ytdl.extract_info(url, download=False)
                playlist_dict = await bot.loop.run_in_executor(None, extract_playlist_info)
                
                if 'entries' not in playlist_dict:
                    await ctx.send('This URL does not appear to be a playlist.')
                    return
                    
                entries = playlist_dict['entries']
                total_songs = len(entries)
                
                if total_songs == 0:
                    await ctx.send('No songs found in this playlist.')
                    return
                    
                await ctx.send(f"Found {total_songs} songs in the playlist. Adding them to the queue...")
                
                status_message = await ctx.send(f"Added 0 / {total_songs} songs")
                
                # Prepare all playlist items
                songs_to_add = []
                for index, entry in enumerate(entries, start=1):
                    if 'title' in entry and 'url' in entry:
                        songs_to_add.append((entry['title'], entry['url']))
                    
                    if index % 5 == 0 or index == total_songs:
                        await status_message.edit(content=f"Added {index} / {total_songs} songs")
                    
                    # Small delay to prevent flooding
                    await asyncio.sleep(0.1)
                
                # Add all songs to queue
                queue_manager.add_list(songs_to_add)
                await ctx.send('Playlist fully added to queue.')
                
                # Start playing if not already
                if not player.is_playing:
                    await player._play_next(ctx)
                    
            except Exception as e:
                await ctx.send(f'An error occurred: {str(e)}')
    
    @bot.command(name='pause', help='Pause the current song')
    async def pause_command(ctx):
        """Pause the current song"""
        await player.pause(ctx)
    
    @bot.command(name='resume', help='Resume the paused song')
    async def resume_command(ctx):
        """Resume the paused song"""
        await player.resume(ctx)
    
    @bot.command(name='skip', help='Skip the current song')
    async def skip_command(ctx):
        """Skip the current song"""
        await player.skip(ctx)
    
    @bot.command(name='tskip', help='Skip to a specific timestamp (format mm:ss or m:ss)')
    async def timestamp_skip_command(ctx, timestamp):
        """Skip to a specific timestamp in the current song"""
        await player.timestamp_skip(ctx, timestamp)
    
    @bot.command(name='qlist', help='Display the current queue')
    async def queue_list_command(ctx):
        """Display the current queue"""
        if queue_manager.is_empty:
            await ctx.send('The queue is empty.')
            return
            
        queue_items = queue_manager.queue
        queue_list = []
        
        for index, item in enumerate(queue_items):
            title, _ = item
            queue_list.append(f'{index + 1}: {title}')
        
        # Add currently playing song at the top if there is one
        current = queue_manager.current
        if current:
            title, _ = current
            queue_message = f'**Now Playing:** {title}\n\n**Up Next:**\n'
        else:
            queue_message = '**Queue:**\n'
            
        queue_message += '\n'.join(queue_list)
        
        # Split message if too long
        if len(queue_message) > 2000:
            parts = []
            current_part = queue_message[:2000]
            last_newline = current_part.rfind('\n')
            parts.append(current_part[:last_newline])
            
            remaining = queue_message[last_newline+1:]
            await ctx.send(parts[0])
            # Count how many lines are left without using '\n' in f-string
            remaining_lines = remaining.count('\n') + 1
            await ctx.send(f"...and {remaining_lines} more songs")
        else:
            await ctx.send(queue_message)
    
    @bot.command(name='qskip', help='Skip to a specific song in the queue')
    async def queue_skip_command(ctx, index: int):
        """Skip to a specific song in the queue"""
        if queue_manager.is_empty:
            await ctx.send('The queue is empty.')
            return
        
        if index < 1 or index > queue_manager.length:
            await ctx.send('Invalid song index. Please enter a number within the range of the queue.')
            return
        
        # Skip to the specified position
        queue_manager.skip_to(index)
        
        # Stop current playback to trigger next song
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send(f'Skipped to song {index} in the queue.')
        else:
            await player._play_next(ctx)
    
    @bot.command(name='qclear', help='Clear the entire queue')
    async def clear_queue_command(ctx):
        """Clear the entire queue"""
        if queue_manager.is_empty:
            await ctx.send('The queue is already empty.')
            return
            
        queue_manager.clear()
        
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            
        await ctx.send('Queue cleared.')
    
    @bot.command(name='shuffle', help='Shuffle the remaining songs in the queue')
    async def shuffle_command(ctx):
        """Shuffle the remaining songs in the queue"""
        if queue_manager.length < 2:
            await ctx.send('Not enough songs in the queue to shuffle.')
            return
        
        queue_manager.shuffle()
        await ctx.send('Queue shuffled successfully.')
    
    @bot.command(name='leave', help='Make the bot leave the voice channel')
    async def leave_command(ctx):
        """Make the bot leave the voice channel"""
        await player.leave(ctx)
    
    @bot.command(name='reconnect', help='Reconnect to voice channel if connection is lost')
    async def reconnect_command(ctx):
        """Reconnect to voice channel"""
        if not ctx.author.voice:
            await ctx.send(f"{ctx.author.name} is not connected to a voice channel")
            return
        
        # Force disconnect first
        if ctx.voice_client:
            try:
                await ctx.voice_client.disconnect(force=True)
                await asyncio.sleep(1)
            except Exception:
                pass
        
        # Reconnect
        voice_client = await player.connect_to_voice(ctx)
        if voice_client:
            await ctx.send("Successfully reconnected to voice channel!")
        else:
            await ctx.send("Failed to reconnect to voice channel.") 