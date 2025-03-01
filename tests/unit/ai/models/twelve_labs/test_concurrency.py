"""Tests for TwelveLabsModel concurrent request handling."""

from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from .conftest import create_mock_response


class ThreadSafeCounter:
    def __init__(self):
        self.value = 0
        self.lock = Lock()

    def increment(self):
        with self.lock:
            self.value += 1


def test_concurrent_requests(model, mock_session):
    """Test handling of concurrent API requests.

    Scenario:
        - Make multiple concurrent requests using thread pool
        - Track number of requests made
        - Ensure thread safety of request counting

    Expected Behavior:
        - All requests complete successfully
        - Request count matches number of requests made
        - No race conditions in request handling
        - Thread pool manages concurrent execution
    """
    request_count = ThreadSafeCounter()

    def mock_request(*args, **kwargs):
        request_count.increment()
        return create_mock_response(status_code=200, json_data={"status": "success"})

    mock_session.request.side_effect = mock_request

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(model._make_request, "GET", "/test") for _ in range(5)
        ]
        results = [f.result() for f in futures]

    assert len(results) == 5
    assert request_count.value == 5
