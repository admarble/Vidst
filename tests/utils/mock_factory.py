"""Mock factory for generating test data."""

from typing import Any


class MockFactory:
    """Factory for generating mock test data."""

    @staticmethod
    def create_video_metadata() -> dict[str, Any]:
        """Create mock video metadata."""
        return {
            "id": "test_video_001",
            "duration": 300,  # 5 minutes
            "fps": 30,
            "resolution": (1920, 1080),
            "format": "mp4",
            "size_bytes": 15_000_000,
        }

    @staticmethod
    def create_scene_data() -> list[dict[str, Any]]:
        """Create mock scene detection data."""
        return [
            {
                "start_time": 0,
                "end_time": 60,
                "confidence": 0.95,
                "type": "presentation",
            },
            {
                "start_time": 60,
                "end_time": 120,
                "confidence": 0.92,
                "type": "code_demo",
            },
        ]

    @staticmethod
    def create_transcription_data() -> dict[str, Any]:
        """Create mock transcription data."""
        return {
            "segments": [
                {
                    "start": 0,
                    "end": 5,
                    "text": "Welcome to this tutorial.",
                    "speaker": "speaker_1",
                    "confidence": 0.98,
                },
                {
                    "start": 5,
                    "end": 10,
                    "text": "Let's look at some code examples.",
                    "speaker": "speaker_1",
                    "confidence": 0.96,
                },
            ],
            "speakers": ["speaker_1"],
            "language": "en",
        }

    @staticmethod
    def create_gpt4v_response() -> dict[str, Any]:
        """Create mock GPT-4V response."""
        return {
            "query": "What is shown at 2:30?",
            "response": "At 2:30, the video shows a code example demonstrating a Python function.",
            "confidence": 0.89,
            "context": {
                "timestamp": 150,
                "scene_type": "code_demo",
                "detected_text": ["def example_function():", "    return True"],
            },
        }
