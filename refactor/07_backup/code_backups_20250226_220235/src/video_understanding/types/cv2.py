"""OpenCV constants and types for video processing."""

import sys
from pathlib import Path
from typing import Any, Dict, Union

# Type aliases to avoid circular references
VideoCaptureType = Any  # Represents cv2.VideoCapture
VideoWriterType = Any   # Represents cv2.VideoWriter

# Get cv2 module (real or mock)
cv2 = sys.modules.get("cv2")
if cv2 is None:
    import cv2

# Re-export OpenCV classes and functions with lazy initialization
def _get_cv2_attr(name: str) -> Any:
    """Get cv2 attribute with lazy initialization."""
    return getattr(cv2, name)

VideoCapture = lambda *args, **kwargs: _get_cv2_attr("VideoCapture")(*args, **kwargs)
VideoWriter = lambda *args, **kwargs: _get_cv2_attr("VideoWriter")(*args, **kwargs)
imread = lambda *args, **kwargs: _get_cv2_attr("imread")(*args, **kwargs)
imwrite = lambda *args, **kwargs: _get_cv2_attr("imwrite")(*args, **kwargs)
resize = lambda *args, **kwargs: _get_cv2_attr("resize")(*args, **kwargs)
cvtColor = lambda *args, **kwargs: _get_cv2_attr("cvtColor")(*args, **kwargs)

def create_video_capture(video_path: Union[str, Path]) -> VideoCaptureType:
    """Create a VideoCapture object for the given video path.

    Args:
        video_path: Path to the video file

    Returns:
        VideoCapture object

    Raises:
        ValueError: If video file cannot be opened
    """
    cap = VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    return cap

def get_video_properties(cap: VideoCaptureType) -> Dict[str, Union[int, float]]:
    """Get video properties from a VideoCapture object.

    Args:
        cap: VideoCapture object

    Returns:
        Dictionary containing video properties
    """
    return {
        "width": int(cap.get(_get_cv2_attr("CAP_PROP_FRAME_WIDTH"))),
        "height": int(cap.get(_get_cv2_attr("CAP_PROP_FRAME_HEIGHT"))),
        "fps": float(cap.get(_get_cv2_attr("CAP_PROP_FPS"))),
        "frame_count": int(cap.get(_get_cv2_attr("CAP_PROP_FRAME_COUNT"))),
        "fourcc": int(cap.get(_get_cv2_attr("CAP_PROP_FOURCC"))),
    }

# Lazy property getters
def _get_property(name: str) -> int:
    return getattr(cv2, name)

# Video capture properties
CAP_PROP_POS_MSEC = lambda: _get_property("CAP_PROP_POS_MSEC")
CAP_PROP_POS_FRAMES = lambda: _get_property("CAP_PROP_POS_FRAMES")
CAP_PROP_POS_AVI_RATIO = lambda: _get_property("CAP_PROP_POS_AVI_RATIO")
CAP_PROP_FRAME_WIDTH = lambda: _get_property("CAP_PROP_FRAME_WIDTH")
CAP_PROP_FRAME_HEIGHT = lambda: _get_property("CAP_PROP_FRAME_HEIGHT")
CAP_PROP_FPS = lambda: _get_property("CAP_PROP_FPS")
CAP_PROP_FOURCC = lambda: _get_property("CAP_PROP_FOURCC")
CAP_PROP_FRAME_COUNT = lambda: _get_property("CAP_PROP_FRAME_COUNT")
CAP_PROP_FORMAT = lambda: _get_property("CAP_PROP_FORMAT")
CAP_PROP_MODE = lambda: _get_property("CAP_PROP_MODE")
CAP_PROP_BRIGHTNESS = lambda: _get_property("CAP_PROP_BRIGHTNESS")
CAP_PROP_CONTRAST = lambda: _get_property("CAP_PROP_CONTRAST")
CAP_PROP_SATURATION = lambda: _get_property("CAP_PROP_SATURATION")
CAP_PROP_HUE = lambda: _get_property("CAP_PROP_HUE")
CAP_PROP_GAIN = lambda: _get_property("CAP_PROP_GAIN")
CAP_PROP_EXPOSURE = lambda: _get_property("CAP_PROP_EXPOSURE")

# Color conversion codes
COLOR_BGR2GRAY = lambda: _get_property("COLOR_BGR2GRAY")
COLOR_RGB2GRAY = lambda: _get_property("COLOR_RGB2GRAY")
COLOR_GRAY2BGR = lambda: _get_property("COLOR_GRAY2BGR")
COLOR_GRAY2RGB = lambda: _get_property("COLOR_GRAY2RGB")
COLOR_BGR2RGB = lambda: _get_property("COLOR_BGR2RGB")
COLOR_RGB2BGR = lambda: _get_property("COLOR_RGB2BGR")

# Window properties
WINDOW_NORMAL = lambda: _get_property("WINDOW_NORMAL")
WINDOW_AUTOSIZE = lambda: _get_property("WINDOW_AUTOSIZE")
WINDOW_OPENGL = lambda: _get_property("WINDOW_OPENGL")

# Mouse events
EVENT_MOUSEMOVE = lambda: _get_property("EVENT_MOUSEMOVE")
EVENT_LBUTTONDOWN = lambda: _get_property("EVENT_LBUTTONDOWN")
EVENT_RBUTTONDOWN = lambda: _get_property("EVENT_RBUTTONDOWN")
EVENT_MBUTTONDOWN = lambda: _get_property("EVENT_MBUTTONDOWN")
EVENT_LBUTTONUP = lambda: _get_property("EVENT_LBUTTONUP")
EVENT_RBUTTONUP = lambda: _get_property("EVENT_RBUTTONUP")
EVENT_MBUTTONUP = lambda: _get_property("EVENT_MBUTTONUP")
EVENT_LBUTTONDBLCLK = lambda: _get_property("EVENT_LBUTTONDBLCLK")
EVENT_RBUTTONDBLCLK = lambda: _get_property("EVENT_RBUTTONDBLCLK")
EVENT_MBUTTONDBLCLK = lambda: _get_property("EVENT_MBUTTONDBLCLK")

# Interpolation methods
INTER_NEAREST = lambda: _get_property("INTER_NEAREST")
INTER_LINEAR = lambda: _get_property("INTER_LINEAR")
INTER_CUBIC = lambda: _get_property("INTER_CUBIC")
INTER_AREA = lambda: _get_property("INTER_AREA")
INTER_LANCZOS4 = lambda: _get_property("INTER_LANCZOS4")

# Border types
BORDER_CONSTANT = lambda: _get_property("BORDER_CONSTANT")
BORDER_REPLICATE = lambda: _get_property("BORDER_REPLICATE")
BORDER_REFLECT = lambda: _get_property("BORDER_REFLECT")
BORDER_WRAP = lambda: _get_property("BORDER_WRAP")
BORDER_REFLECT_101 = lambda: _get_property("BORDER_REFLECT_101")
BORDER_TRANSPARENT = lambda: _get_property("BORDER_TRANSPARENT")
BORDER_DEFAULT = lambda: _get_property("BORDER_DEFAULT")
BORDER_ISOLATED = lambda: _get_property("BORDER_ISOLATED")

# Update __all__ to include all exported names
__all__ = [
    # OpenCV classes and functions
    "VideoCapture",
    "VideoWriter",
    "imread",
    "imwrite",
    "resize",
    "cvtColor",
    "create_video_capture",
    "get_video_properties",

    # Video capture properties
    "CAP_PROP_POS_MSEC",
    "CAP_PROP_POS_FRAMES",
    "CAP_PROP_POS_AVI_RATIO",
    "CAP_PROP_FRAME_WIDTH",
    "CAP_PROP_FRAME_HEIGHT",
    "CAP_PROP_FPS",
    "CAP_PROP_FOURCC",
    "CAP_PROP_FRAME_COUNT",
    "CAP_PROP_FORMAT",
    "CAP_PROP_MODE",
    "CAP_PROP_BRIGHTNESS",
    "CAP_PROP_CONTRAST",
    "CAP_PROP_SATURATION",
    "CAP_PROP_HUE",
    "CAP_PROP_GAIN",
    "CAP_PROP_EXPOSURE",

    # Color conversion codes
    "COLOR_BGR2GRAY",
    "COLOR_RGB2GRAY",
    "COLOR_GRAY2BGR",
    "COLOR_GRAY2RGB",
    "COLOR_BGR2RGB",
    "COLOR_RGB2BGR",

    # Window properties
    "WINDOW_NORMAL",
    "WINDOW_AUTOSIZE",
    "WINDOW_OPENGL",

    # Mouse events
    "EVENT_MOUSEMOVE",
    "EVENT_LBUTTONDOWN",
    "EVENT_RBUTTONDOWN",
    "EVENT_MBUTTONDOWN",
    "EVENT_LBUTTONUP",
    "EVENT_RBUTTONUP",
    "EVENT_MBUTTONUP",
    "EVENT_LBUTTONDBLCLK",
    "EVENT_RBUTTONDBLCLK",
    "EVENT_MBUTTONDBLCLK",

    # Interpolation methods
    "INTER_NEAREST",
    "INTER_LINEAR",
    "INTER_CUBIC",
    "INTER_AREA",
    "INTER_LANCZOS4",

    # Border types
    "BORDER_CONSTANT",
    "BORDER_REPLICATE",
    "BORDER_REFLECT",
    "BORDER_WRAP",
    "BORDER_REFLECT_101",
    "BORDER_TRANSPARENT",
    "BORDER_DEFAULT",
    "BORDER_ISOLATED",
]
