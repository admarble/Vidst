import pytest
from unittest.mock import Mock, patch
import numpy as np
from src.core.processing.detection import SceneDetector, ObjectDetector

class TestSceneDetection:
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.frame_data = np.zeros((1920, 1080, 3), dtype=np.uint8)
        self.test_video_path = "tests/fixtures/sample_video.mp4"

    def test_scene_boundary_detection(self):
        """Test detection of scene boundaries."""
        with patch('cv2.VideoCapture') as mock_capture:
            mock_capture.return_value.read.return_value = (True, self.frame_data)
            detector = SceneDetector()
            scenes = detector.detect_scenes(self.test_video_path)
            assert len(scenes) > 0
            assert all(isinstance(scene, dict) for scene in scenes)
            assert all("start_time" in scene for scene in scenes)

    def test_minimum_scene_length(self):
        """Test enforcement of minimum scene length."""
        detector = SceneDetector(min_scene_length=2.0)
        scenes = detector.detect_scenes(self.test_video_path)
        scene_lengths = [scene["end_time"] - scene["start_time"] for scene in scenes]
        assert all(length >= 2.0 for length in scene_lengths)

    def test_maximum_scenes_limit(self):
        """Test enforcement of maximum scenes limit."""
        detector = SceneDetector(max_scenes=5)
        scenes = detector.detect_scenes(self.test_video_path)
        assert len(scenes) <= 5

class TestObjectDetection:
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.frame = np.zeros((1920, 1080, 3), dtype=np.uint8)

    def test_object_detection_results(self):
        """Test basic object detection functionality."""
        detector = ObjectDetector()
        results = detector.detect_objects(self.frame)
        assert isinstance(results, list)
        for obj in results:
            assert "label" in obj
            assert "confidence" in obj
            assert "bbox" in obj

    def test_confidence_threshold(self):
        """Test confidence threshold filtering."""
        detector = ObjectDetector(confidence_threshold=0.8)
        results = detector.detect_objects(self.frame)
        assert all(obj["confidence"] >= 0.8 for obj in results)

    def test_batch_processing(self):
        """Test batch processing of frames."""
        frames = [self.frame] * 5
        detector = ObjectDetector()
        batch_results = detector.process_batch(frames)
        assert len(batch_results) == 5
        assert all(isinstance(frame_results, list) for frame_results in batch_results)
