import pytest
from unittest.mock import Mock, patch
import numpy as np
from src.core.processing.scene import SceneAnalyzer, SceneMetadata

class TestSceneAnalyzer:
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.analyzer = SceneAnalyzer()
        self.test_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        self.test_scene = {
            "start_time": 0.0,
            "end_time": 5.0,
            "frames": [self.test_frame] * 10
        }

    def test_scene_content_analysis(self):
        """Test analysis of scene content."""
        result = self.analyzer.analyze_scene(self.test_scene)
        assert isinstance(result, dict)
        assert "content_type" in result
        assert "confidence" in result
        assert "metadata" in result

    def test_scene_transition_detection(self):
        """Test detection of scene transitions."""
        scenes = [self.test_scene, self.test_scene]
        transitions = self.analyzer.analyze_transitions(scenes)
        assert isinstance(transitions, list)
        assert len(transitions) == 1  # One transition between two scenes
        assert all("type" in t for t in transitions)

    def test_scene_duration_validation(self):
        """Test validation of scene duration."""
        invalid_scene = {
            "start_time": 0.0,
            "end_time": 0.5,  # Too short
            "frames": [self.test_frame]
        }
        with pytest.raises(ValueError):
            self.analyzer.analyze_scene(invalid_scene)

class TestSceneMetadata:
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.metadata = SceneMetadata()
        self.test_data = {
            "duration": 5.0,
            "frame_count": 150,
            "average_brightness": 0.5
        }

    def test_metadata_creation(self):
        """Test creation of scene metadata."""
        meta = self.metadata.create(self.test_data)
        assert isinstance(meta, dict)
        assert "duration" in meta
        assert "frame_count" in meta
        assert "timestamp" in meta

    def test_metadata_validation(self):
        """Test validation of metadata fields."""
        invalid_data = {
            "duration": -1.0,  # Invalid duration
            "frame_count": 150
        }
        with pytest.raises(ValueError):
            self.metadata.create(invalid_data)

    def test_metadata_aggregation(self):
        """Test aggregation of metadata from multiple scenes."""
        scene_list = [self.test_data] * 3
        aggregated = self.metadata.aggregate(scene_list)
        assert isinstance(aggregated, dict)
        assert "total_duration" in aggregated
        assert "total_frames" in aggregated
        assert aggregated["total_frames"] == 450  # 3 * 150
