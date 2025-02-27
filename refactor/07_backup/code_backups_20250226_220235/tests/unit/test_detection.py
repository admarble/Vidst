import pytest
from unittest.mock import Mock, patch
import numpy as np
from pathlib import Path
from video_understanding.core.upload.scene import SceneDetector
from video_understanding.core.upload.detection import ObjectDetector, DetectedObject
import cv2

class TestSceneDetection:
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.frame_data = np.zeros((1920, 1080, 3), dtype=np.uint8)
        self.test_video_path = Path("tests/fixtures/sample_video.mp4")

    @pytest.mark.asyncio
    async def test_scene_boundary_detection(self):
        """Test detection of scene boundaries."""
        with patch('cv2.VideoCapture') as mock_capture:
            mock_capture.return_value.read.return_value = (True, self.frame_data)
            mock_capture.return_value.get.side_effect = lambda prop: {
                cv2.CAP_PROP_FPS: 30.0,
                cv2.CAP_PROP_FRAME_COUNT: 300
            }.get(prop, 0)

            detector = SceneDetector()
            scenes = await detector.detect(self.test_video_path)

            assert isinstance(scenes, list)
            assert all(isinstance(scene, dict) for scene in scenes)
            assert all("start_time" in scene for scene in scenes)
            assert all("end_time" in scene for scene in scenes)

    @pytest.mark.asyncio
    async def test_minimum_scene_length(self):
        """Test enforcement of minimum scene length."""
        detector = SceneDetector()
        detector.set_min_scene_duration(2.0)

        with patch('cv2.VideoCapture') as mock_capture:
            mock_capture.return_value.read.return_value = (True, self.frame_data)
            mock_capture.return_value.get.side_effect = lambda prop: {
                cv2.CAP_PROP_FPS: 30.0,
                cv2.CAP_PROP_FRAME_COUNT: 300
            }.get(prop, 0)

            scenes = await detector.detect(self.test_video_path)
            scene_lengths = [scene["end_time"] - scene["start_time"] for scene in scenes]
            assert all(length >= 2.0 for length in scene_lengths)

    @pytest.mark.asyncio
    async def test_maximum_scenes_limit(self):
        """Test enforcement of maximum scenes limit."""
        detector = SceneDetector()
        detector.set_max_scenes(5)

        with patch('cv2.VideoCapture') as mock_capture:
            mock_capture.return_value.read.return_value = (True, self.frame_data)
            mock_capture.return_value.get.side_effect = lambda prop: {
                cv2.CAP_PROP_FPS: 30.0,
                cv2.CAP_PROP_FRAME_COUNT: 300
            }.get(prop, 0)

            scenes = await detector.detect(self.test_video_path)
            assert len(scenes) <= 5

class TestObjectDetection:
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a test frame with proper dimensions and format
        self.frame = np.zeros((480, 640, 3), dtype=np.uint8)  # Standard VGA size
        # Add a simple shape to the frame
        cv2.rectangle(self.frame, (100, 100), (200, 200), (255, 255, 255), -1)

    @patch('ultralytics.YOLO')
    def test_object_detection_results(self, mock_yolo):
        """Test basic object detection functionality."""
        # Mock YOLO results
        mock_results = Mock()
        mock_box = Mock()
        mock_box.conf = Mock(item=lambda: 0.9)
        mock_box.cls = Mock(item=lambda: 0)
        mock_box.xyxy = [np.array([10, 20, 30, 40])]
        mock_results.boxes = [mock_box]
        mock_results.names = {0: "person"}
        mock_yolo.return_value.return_value = [mock_results]

        detector = ObjectDetector()
        results = detector.detect_objects(self.frame)

        assert isinstance(results, list)
        assert len(results) > 0
        assert isinstance(results[0], DetectedObject)
        assert results[0].label == "person"
        assert results[0].confidence == 0.9
        assert len(results[0].bbox) == 4

    @patch('ultralytics.YOLO')
    def test_confidence_threshold(self, mock_yolo):
        """Test confidence threshold filtering."""
        # Mock YOLO results
        mock_results = Mock()
        mock_box = Mock()
        mock_box.conf = Mock(item=lambda: 0.85)
        mock_box.cls = Mock(item=lambda: 0)
        mock_box.xyxy = [np.array([10, 20, 30, 40])]
        mock_results.boxes = [mock_box]
        mock_results.names = {0: "person"}
        mock_yolo.return_value.return_value = [mock_results]

        detector = ObjectDetector(confidence_threshold=0.8)
        results = detector.detect_objects(self.frame)
        assert all(obj.confidence >= 0.8 for obj in results)
