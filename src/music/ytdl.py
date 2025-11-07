"""
YouTube downloader module for the Discord music bot.
"""
import asyncio
import discord
import yt_dlp as youtube_dl
from src.config import YTDL_FORMAT_OPTIONS, FFMPEG_OPTIONS

# Suppress bug reports from youtube_dl
youtube_dl.utils.bug_reports_message = lambda: ''

class YTDLSource(discord.PCMVolumeTransformer):
    """
    Custom audio source class for YouTube downloads
    """
    # Create YouTube downloader instance as class variable
    ytdl = youtube_dl.YoutubeDL(YTDL_FORMAT_OPTIONS)
    
    def __init__(self, source, *, data, volume=1.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title', 'Unknown title')
        self.url = data.get('url', '')
        self.webpage_url = data.get('webpage_url', data.get('url', ''))
        self.duration = data.get('duration', 0)

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False, timestamp=0, retries=3):
        """
        Create a YTDLSource from a URL with optional timestamp and retries.
        
        Args:
            url (str): The YouTube URL to play
            loop (asyncio.AbstractEventLoop, optional): Event loop to use
            stream (bool, optional): Whether to stream or download. Defaults to False.
            timestamp (int, optional): Start time in seconds. Defaults to 0.
            retries (int, optional): Number of retries on failure. Defaults to 3.
            
        Returns:
            YTDLSource: Audio source object for Discord
        """
        loop = loop or asyncio.get_event_loop()
        
        for attempt in range(retries):
            try:
                # Extract info from YouTube with better error handling
                def extract_data():
                    try:
                        return cls.ytdl.extract_info(url, download=not stream)
                    except Exception as e:
                        if "Sign in to confirm your age" in str(e) or "Private video" in str(e):
                            raise Exception(f"Video unavailable: {e}")
                        elif "Video unavailable" in str(e):
                            raise Exception(f"Video not found or deleted: {e}")
                        else:
                            raise e
                data = await loop.run_in_executor(None, extract_data)
                
                if 'entries' in data:
                    # Take first item from a playlist
                    data = data['entries'][0]
                    
                # Get filename or direct URL
                filename = data['url'] if stream else cls.ytdl.prepare_filename(data)
                
                # Apply timestamp if provided
                custom_ffmpeg_options = FFMPEG_OPTIONS.copy()
                if timestamp > 0:
                    if stream:
                        # For streaming, timestamp needs to be in before_options
                        current_before = custom_ffmpeg_options.get('before_options', '')
                        custom_ffmpeg_options['before_options'] = f"{current_before} -ss {timestamp}".strip()
                    else:
                        # For downloaded files, timestamp can be in options
                        current_options = custom_ffmpeg_options.get('options', '')
                        custom_ffmpeg_options['options'] = f"{current_options} -ss {timestamp}".strip()
                
                # Create FFmpeg audio source with better performance using Opus
                # Fix parameter names for discord.py FFmpeg classes
                # FFmpegOpusAudio.from_probe() expects 'before' parameter
                # FFmpegPCMAudio() constructor expects 'before_options' parameter
                
                try:
                    # Try FFmpegOpusAudio first for better performance
                    opus_params = custom_ffmpeg_options.copy()
                    if 'before_options' in opus_params:
                        opus_params['before'] = opus_params.pop('before_options')
                    
                    audio_source = await discord.FFmpegOpusAudio.from_probe(filename, **opus_params)
                    return cls(audio_source, data=data)
                except Exception as opus_error:
                    # Fallback to FFmpegPCMAudio if Opus fails
                    print(f"FFmpegOpusAudio failed, falling back to FFmpegPCMAudio: {opus_error}")
                    
                    # FFmpegPCMAudio uses 'before_options' parameter (keep original)
                    pcm_params = custom_ffmpeg_options.copy()
                    return cls(discord.FFmpegPCMAudio(filename, **pcm_params), data=data)
                
            except Exception as e:
                if attempt == retries - 1:
                    # Provide more helpful error messages
                    error_msg = str(e)
                    if "Video unavailable" in error_msg or "Private video" in error_msg:
                        raise Exception(f"Cannot play this video - it may be private, age-restricted, or deleted: {error_msg}")
                    elif "Sign in to confirm" in error_msg:
                        raise Exception("Cannot play age-restricted videos")
                    elif "FFmpeg" in error_msg or "ffmpeg" in error_msg:
                        raise Exception(f"Audio processing error - please check if FFmpeg is properly installed: {error_msg}")
                    else:
                        raise Exception(f"Failed to load audio after {retries} attempts: {error_msg}")
                # Exponential backoff for retries
                await asyncio.sleep(2 ** attempt)

    @classmethod
    async def search_source(cls, search_query, *, loop=None, max_results=5):
        """
        Search for YouTube videos based on a query.
        
        Args:
            search_query (str): The search query
            loop (asyncio.AbstractEventLoop, optional): Event loop to use
            max_results (int, optional): Maximum number of results. Defaults to 5.
            
        Returns:
            tuple: Contains list of entries and formatted result message
        """
        loop = loop or asyncio.get_event_loop()
        
        # Format query for YouTube search
        search_query = f"ytsearch{max_results}:{search_query}"
        
        try:
            def extract_search_data():
                return cls.ytdl.extract_info(search_query, download=False)
            info = await loop.run_in_executor(None, extract_search_data)
            
            if info and 'entries' in info and info['entries']:
                entries = info['entries']
                result_message = ""
                
                for i, entry in enumerate(entries):
                    if entry:  # Check if the entry is not None
                        duration_str = cls._format_duration(entry.get('duration', 0))
                        result_message += f"{i+1}: {entry.get('title', 'Unknown Title')} ({duration_str})\n"
                
                return entries, result_message
            else:
                return [], "No search results found."
                
        except Exception as e:
            return [], f"An error occurred: {str(e)}"

    @staticmethod
    def _format_duration(duration_seconds):
        """Format duration in seconds to MM:SS format"""
        if not duration_seconds:
            return "Unknown"
            
        minutes, seconds = divmod(int(duration_seconds), 60)
        return f"{minutes}:{seconds:02d}" 