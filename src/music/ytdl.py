"""
YouTube downloader module for the Discord music bot using PyTubeFix.
"""
import asyncio
import discord
from pytubefix import YouTube, Search, Playlist
from pytubefix.exceptions import VideoUnavailable, RegexMatchError, PytubeFixError
from src.config import FFMPEG_OPTIONS


class YTDLSource(discord.PCMVolumeTransformer):
    """
    Custom audio source class for YouTube downloads using PyTubeFix
    """
    
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')
        self.thumbnail = data.get('thumbnail')
        self.uploader = data.get('uploader')
        self.view_count = data.get('view_count')
        self.webpage_url = data.get('webpage_url', data.get('url', ''))
        
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True, timestamp=0, retries=3):
        """
        Create a YTDLSource from a YouTube URL using PyTubeFix
        
        Args:
            url (str): The YouTube URL to play
            loop (asyncio.AbstractEventLoop, optional): Event loop to use
            stream (bool, optional): Whether to stream or download. Defaults to True.
            timestamp (int, optional): Start time in seconds. Defaults to 0.
            retries (int, optional): Number of retries on failure. Defaults to 3.
            
        Returns:
            YTDLSource: Audio source object for Discord
        """
        loop = loop or asyncio.get_event_loop()
        
        for attempt in range(retries):
            try:
                # Extract video information using PyTubeFix
                yt = await loop.run_in_executor(None, YouTube, url)
                
                # Get the best audio stream
                audio_stream = yt.streams.filter(only_audio=True).first()
                if not audio_stream:
                    raise Exception("No audio stream available for this video")
                
                # Get the stream URL
                stream_url = audio_stream.url
                
                # Prepare data dictionary similar to yt-dlp format
                data = {
                    'title': yt.title,
                    'url': stream_url,
                    'duration': yt.length,
                    'thumbnail': yt.thumbnail_url,
                    'uploader': yt.author,
                    'view_count': yt.views,
                    'webpage_url': url
                }
                
                # Use custom FFmpeg options from config
                custom_ffmpeg_options = FFMPEG_OPTIONS.copy()
                
                # Apply timestamp if provided
                if timestamp > 0:
                    current_before = custom_ffmpeg_options.get('before_options', '')
                    custom_ffmpeg_options['before_options'] = f"{current_before} -ss {timestamp}".strip()
                
                try:
                    print(f"Creating FFmpegPCMAudio for: {data.get('title', 'Unknown')}")
                    audio_source = discord.FFmpegPCMAudio(stream_url, **custom_ffmpeg_options)
                    print(f"Successfully created FFmpegPCMAudio for: {data.get('title', 'Unknown')}")
                    return cls(audio_source, data=data)
                except TypeError as type_error:
                    print(f"TypeError in FFmpegPCMAudio (parameter issue): {type_error}")
                    print(f"Parameters passed: {custom_ffmpeg_options}")
                    try:
                        print("Attempting with minimal parameters...")
                        audio_source = discord.FFmpegPCMAudio(stream_url)
                        return cls(audio_source, data=data)
                    except Exception as minimal_error:
                        print(f"Even minimal FFmpegPCMAudio failed: {minimal_error}")
                        raise Exception(f"FFmpeg parameter error: {type_error}")
                except Exception as ffmpeg_error:
                    print(f"FFmpegPCMAudio failed with general error: {ffmpeg_error}")
                    print(f"Error type: {type(ffmpeg_error)}")
                    raise Exception(f"Failed to create audio source: {ffmpeg_error}")
                    
            except VideoUnavailable as e:
                raise Exception(f"Video is unavailable: {str(e)}")
            except RegexMatchError as e:
                raise Exception(f"Invalid YouTube URL: {str(e)}")
            except PytubeFixError as e:
                print(f"PyTubeFix error on attempt {attempt + 1}: {e}")
                if attempt == retries - 1:
                    raise Exception(f"Failed to load video after {retries} attempts: {str(e)}")
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt == retries - 1:
                    # Provide more helpful error messages
                    error_msg = str(e)
                    if "age-restricted" in error_msg.lower() or "sign in" in error_msg.lower():
                        raise Exception("This video is age-restricted or requires authentication")
                    elif "FFmpeg" in error_msg or "ffmpeg" in error_msg:
                        raise Exception(f"Audio processing error - please check if FFmpeg is properly installed: {error_msg}")
                    else:
                        raise Exception(f"Failed to load audio after {retries} attempts: {error_msg}")
                # Exponential backoff for retries
                await asyncio.sleep(2 ** attempt)
    
    @classmethod
    async def search_source(cls, search_query, *, loop=None, max_results=5):
        """
        Search for YouTube videos and return results using PyTubeFix
        
        Args:
            search_query (str): The search query
            loop (asyncio.AbstractEventLoop, optional): Event loop to use
            max_results (int, optional): Maximum number of results. Defaults to 5.
            
        Returns:
            tuple: Contains list of entries and formatted result message
        """
        loop = loop or asyncio.get_event_loop()
        
        try:
            # Search for videos using PyTubeFix
            search = await loop.run_in_executor(None, Search, search_query)
            results = []
            result_message = ""
            
            # Get up to max_results results
            for i, video in enumerate(search.results[:max_results]):
                try:
                    result_data = {
                        'title': video.title,
                        'url': video.watch_url,
                        'duration': video.length,
                        'thumbnail': video.thumbnail_url,
                        'uploader': video.author,
                        'view_count': video.views,
                        'webpage_url': video.watch_url
                    }
                    results.append(result_data)
                    
                    # Format duration for display
                    duration_str = cls._format_duration(video.length)
                    result_message += f"{i+1}: {video.title} ({duration_str})\n"
                    
                except Exception as e:
                    print(f"Error processing search result {i}: {e}")
                    continue
            
            return results, result_message if results else "No search results found."
                
        except Exception as e:
            print(f"Search failed: {e}")
            return [], f"An error occurred: {str(e)}"
    
    @classmethod
    async def get_playlist(cls, url, *, loop=None, limit=30):
        """
        Extract playlist information from YouTube using PyTubeFix
        
        Args:
            url (str): The YouTube playlist URL
            loop (asyncio.AbstractEventLoop, optional): Event loop to use
            limit (int, optional): Maximum number of videos to extract. Defaults to 30.
            
        Returns:
            dict: Playlist information with entries, or None if failed
        """
        loop = loop or asyncio.get_event_loop()
        
        try:
            # Extract playlist information using PyTubeFix
            playlist = await loop.run_in_executor(None, Playlist, url)
            
            entries = []
            for i, video in enumerate(playlist.videos[:limit]):
                try:
                    entry_data = {
                        'title': video.title,
                        'url': video.watch_url,
                        'duration': video.length,
                        'thumbnail': video.thumbnail_url,
                        'uploader': video.author,
                        'view_count': video.views,
                        'webpage_url': video.watch_url
                    }
                    entries.append(entry_data)
                except Exception as e:
                    print(f"Error processing playlist video {i}: {e}")
                    continue
            
            return {
                'title': playlist.title or 'Unknown Playlist',
                'entries': entries,
                'uploader': playlist.owner or 'Unknown',
                'entry_count': len(entries)
            }
                
        except Exception as e:
            print(f"Playlist extraction failed: {e}")
            return None
    
    @staticmethod
    def _format_duration(duration_seconds):
        """Format duration in seconds to MM:SS format"""
        if not duration_seconds:
            return "Unknown"
            
        minutes, seconds = divmod(int(duration_seconds), 60)
        return f"{minutes}:{seconds:02d}"