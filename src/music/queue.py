"""
Queue management module for Discord music bot.
"""
import asyncio
import random
from typing import List, Tuple, Optional, Callable, Any

class MusicQueue:
    """
    Manages the queue of songs to be played.
    """
    def __init__(self):
        """Initialize an empty music queue"""
        self._queue: List[Tuple[str, str]] = []  # List of (title, url) tuples
        self._current_item: Optional[Tuple[str, str]] = None
    
    @property
    def current(self) -> Optional[Tuple[str, str]]:
        """Returns the currently playing item"""
        return self._current_item
    
    @property
    def queue(self) -> List[Tuple[str, str]]:
        """Returns a copy of the queue"""
        return self._queue.copy()
    
    @property
    def is_empty(self) -> bool:
        """Check if the queue is empty"""
        return len(self._queue) == 0
    
    @property
    def length(self) -> int:
        """Returns the number of items in the queue"""
        return len(self._queue)
    
    def add(self, title: str, url: str) -> None:
        """
        Add an item to the queue
        
        Args:
            title (str): Song title
            url (str): Song URL
        """
        self._queue.append((title, url))
    
    def add_to_front(self, title: str, url: str, timestamp: Optional[int] = None) -> None:
        """
        Add an item to the front of the queue
        
        Args:
            title (str): Song title
            url (str): Song URL
            timestamp (Optional[int]): Timestamp in seconds to start playback from
        """
        # We store the timestamp as a third element in the tuple for the from_url method to use
        if timestamp is not None:
            self._queue.insert(0, (title, url, timestamp))
        else:
            self._queue.insert(0, (title, url))
    
    def add_list(self, items: List[Tuple[str, str]]) -> None:
        """
        Add multiple items to the queue
        
        Args:
            items (List[Tuple[str, str]]): List of (title, url) tuples to add
        """
        self._queue.extend(items)
    
    def clear(self) -> None:
        """Clear the queue"""
        self._queue = []
        self._current_item = None
    
    def shuffle(self) -> None:
        """Shuffle the queue"""
        if len(self._queue) > 1:
            random.shuffle(self._queue)
    
    def remove(self, index: int) -> Optional[Tuple[str, str]]:
        """
        Remove and return an item at the given index
        
        Args:
            index (int): Index of the item to remove (0-based)
            
        Returns:
            Optional[Tuple[str, str]]: The removed item, or None if index is invalid
        """
        if 0 <= index < len(self._queue):
            return self._queue.pop(index)
        return None
    
    def skip_to(self, index: int) -> None:
        """
        Skip to a specific position in the queue
        
        Args:
            index (int): Index to skip to (1-based)
        """
        if 1 <= index <= len(self._queue):
            # Remove everything before the target index
            del self._queue[:index - 1]
    
    async def get_next(self) -> Optional[Tuple[str, str]]:
        """
        Get the next item from the queue
        
        Returns:
            Optional[Tuple[str, str]]: The next item in the queue, or None if empty
        """
        if self._queue:
            next_item = self._queue.pop(0)
            # Check if it's a timestamped item (has 3 elements)
            if len(next_item) == 3:
                title, url, timestamp = next_item
                # Store just title and URL as the current item
                self._current_item = (title, url)
                # But return all three elements for processing
                return (title, url, timestamp)
            else:
                # Standard item, store and return as usual
                self._current_item = next_item
                return next_item
        
        self._current_item = None
        return None

# Singleton instance
queue_manager = MusicQueue() 