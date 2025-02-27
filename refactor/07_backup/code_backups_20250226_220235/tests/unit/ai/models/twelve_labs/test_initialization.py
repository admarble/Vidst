"""Tests for TwelveLabs model initialization."""

import pytest

from video_understanding.ai.exceptions import ValidationError
from video_understanding.ai.models.twelve_labs import TwelveLabsModel


def test_model_initialization():
    """Test model initialization."""
    model = TwelveLabsModel(api_key="test_key")
    assert model.api_key == "test_key"
    assert model._client is not None


def test_model_initialization_no_api_key():
    """Test model initialization with no API key."""
    with pytest.raises(ValidationError, match="API key is required"):
        TwelveLabsModel("")
