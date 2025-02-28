import asyncio
import random
from functools import wraps
from typing import TypeVar, Callable, Any
from loguru import logger

T = TypeVar('T')


def async_retry(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0, backoff_factor: float = 2.0, 
                jitter: bool = True, exceptions: tuple = (Exception,)):
    """Decorator for async functions to implement retry logic with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Factor by which the delay increases with each retry
        jitter: Whether to add random jitter to the delay
        exceptions: Tuple of exceptions that trigger a retry
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.error(f"Failed after {max_retries} retries: {str(e)}")
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                    
                    # Add jitter if enabled
                    if jitter:
                        delay = delay * (0.5 + random.random())
                        
                    logger.warning(f"Attempt {attempt + 1}/{max_retries + 1} failed: {str(e)}. Retrying in {delay:.2f}s")
                    await asyncio.sleep(delay)
            
            # This should never be reached due to the raise in the exception handler
            raise last_exception
            
        return wrapper
    
    return decorator
