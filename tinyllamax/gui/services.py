"""Background task execution services with cancellation support.

Provides thread-based execution for long-running operations without blocking the UI.
"""
from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Any


class CancellationToken:
    """Token for cooperative cancellation of background tasks."""
    
    def __init__(self) -> None:
        self._cancelled = False
        self._lock = threading.Lock()
    
    def cancel(self) -> None:
        """Signal that the operation should be cancelled."""
        with self._lock:
            self._cancelled = True
    
    def is_cancelled(self) -> bool:
        """Check if cancellation has been requested."""
        with self._lock:
            return self._cancelled
    
    def check_cancelled(self) -> None:
        """Raise exception if cancelled (for cooperative cancellation)."""
        if self.is_cancelled():
            raise CancellationError("Operation was cancelled")


class CancellationError(Exception):
    """Raised when an operation is cancelled."""
    pass


class BackgroundTask:
    """Manages execution of a function in a background thread."""
    
    def __init__(
        self,
        func: Callable[..., Any],
        on_done: Callable[[Any], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
        on_progress: Callable[[str], None] | None = None,
    ) -> None:
        """Initialize background task.
        
        Args:
            func: Function to execute in background thread
            on_done: Callback when function completes successfully (receives result)
            on_error: Callback when function raises exception (receives exception)
            on_progress: Optional callback for progress updates (receives message)
        """
        self.func = func
        self.on_done = on_done
        self.on_error = on_error
        self.on_progress = on_progress
        self.token = CancellationToken()
        self._thread: threading.Thread | None = None
    
    def start(self, *args: Any, **kwargs: Any) -> None:
        """Start the background task with given arguments."""
        def _run() -> None:
            try:
                # Pass cancellation token if function accepts it
                if "cancel_token" in kwargs:
                    kwargs["cancel_token"] = self.token
                result = self.func(*args, **kwargs)
                if self.on_done and not self.token.is_cancelled():
                    self.on_done(result)
            except CancellationError:
                # Silently handle cancellation
                pass
            except Exception as e:
                if self.on_error and not self.token.is_cancelled():
                    self.on_error(e)
        
        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()
    
    def cancel(self) -> None:
        """Request cancellation of the background task."""
        self.token.cancel()
    
    def is_alive(self) -> bool:
        """Check if the background thread is still running."""
        return self._thread is not None and self._thread.is_alive()


def run_background(
    func: Callable[..., Any],
    on_done: Callable[[Any], None] | None = None,
    on_error: Callable[[Exception], None] | None = None,
    on_progress: Callable[[str], None] | None = None,
    *args: Any,
    **kwargs: Any,
) -> BackgroundTask:
    """Execute a function in a background thread.
    
    Args:
        func: Function to execute
        on_done: Callback when complete (receives result)
        on_error: Callback on error (receives exception)
        on_progress: Optional progress callback (receives message)
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func
        
    Returns:
        BackgroundTask instance for monitoring/cancellation
    """
    task = BackgroundTask(func, on_done, on_error, on_progress)
    task.start(*args, **kwargs)
    return task


__all__ = [
    "CancellationToken",
    "CancellationError",
    "BackgroundTask",
    "run_background",
]
