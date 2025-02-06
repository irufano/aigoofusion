from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from threading import Lock
from typing import Any, Dict, List, Optional

from aigoo_fusion.chat.messages.message import Message


class ChatMemory:
    """In-memory chat messages"""
    def __init__(self):
        self.history = {}  # In-memory storage for chat threads
        self.timestamps = {}  # Timestamps to track last usage of threads
        self.lock = Lock()  # To ensure thread-safety
        self.cleanup_task = None  # Reference to the cleanup timer

    def add_message(self, thread_id, message: Message):
        with self.lock:  # Ensure thread-safe access
            if thread_id not in self.history:
                self.history[thread_id] = []
            self.history[thread_id].append(message)
            # Update the last usage timestamp
            self.timestamps[thread_id] = datetime.now()

            # # Ensure cleanup task is running
            # if self.cleanup_task is None:
            # 	self.start_cleanup_task()

    def remove_oldest_message(self, thread_id: str):
        with self.lock:  # Ensure thread-safe access
            if thread_id in self.history and self.history[thread_id]:
                self.history[thread_id].pop(0)  # Remove the first (oldest) message

    def get_thread_history(
        self, thread_id: str, max_length: Optional[int] = None
    ) -> List[Message]:
        with self.lock:  # Ensure thread-safe access
            history = []
            if max_length:
                history = self.history.get(thread_id, [])[:max_length]
            else:
                history = self.history.get(thread_id, [])
            return history

    @asynccontextmanager
    async def intercept(self, thread_id: str, message: Message):
        # Execute before handlers
        self.add_message(thread_id=thread_id, message=message)

        # Create a mutable container to store the result
        result_container: Dict[str, List[Message]] = {"messages": []}
        try:
            yield self.get_thread_history(thread_id=thread_id, max_length=None), result_container
        finally:
            # Execute after handlers
            self.add_message(thread_id=thread_id, message=result_container['messages'][-1]) # type: ignore


