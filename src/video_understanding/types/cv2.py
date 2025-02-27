"""OpenCV constants and types for video processing."""

import cv2
from pathlib import Path
from typing import Union

# Re-export OpenCV classes and functions
VideoCapture = cv2.VideoCapture
VideoWriter = cv2.VideoWriter
imread = cv2.imread
imwrite = cv2.imwrite
resize = cv2.resize
cvtColor = cv2.cvtColor

def create_video_capture(video_path: Union[str, Path]) -> cv2.VideoCapture:
    """Create a VideoCapture object for the given video path.

    Args:
        video_path: Path to the video file

    Returns:
        VideoCapture object

    Raises:
        ValueError: If video file cannot be opened
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    return cap

def get_video_properties(cap: cv2.VideoCapture) -> dict:
    """Get video properties from a VideoCapture object.

    Args:
        cap: VideoCapture object

    Returns:
        Dictionary containing video properties
    """
    return {
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "fps": float(cap.get(cv2.CAP_PROP_FPS)),
        "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        "fourcc": int(cap.get(cv2.CAP_PROP_FOURCC)),
    }

# Video capture properties
CAP_PROP_POS_MSEC = cv2.CAP_PROP_POS_MSEC  # Current position in milliseconds
CAP_PROP_POS_FRAMES = cv2.CAP_PROP_POS_FRAMES  # Current frame number
CAP_PROP_POS_AVI_RATIO = cv2.CAP_PROP_POS_AVI_RATIO  # Relative position (0=start, 1=end)
CAP_PROP_FRAME_WIDTH = cv2.CAP_PROP_FRAME_WIDTH  # Width of frames
CAP_PROP_FRAME_HEIGHT = cv2.CAP_PROP_FRAME_HEIGHT  # Height of frames
CAP_PROP_FPS = cv2.CAP_PROP_FPS  # Frame rate
CAP_PROP_FOURCC = cv2.CAP_PROP_FOURCC  # Codec FOURCC code
CAP_PROP_FRAME_COUNT = cv2.CAP_PROP_FRAME_COUNT  # Number of frames
CAP_PROP_FORMAT = cv2.CAP_PROP_FORMAT  # Format of the frames
CAP_PROP_MODE = cv2.CAP_PROP_MODE  # Backend-specific value indicating the current capture mode
CAP_PROP_BRIGHTNESS = cv2.CAP_PROP_BRIGHTNESS  # Brightness of the image
CAP_PROP_CONTRAST = cv2.CAP_PROP_CONTRAST  # Contrast of the image
CAP_PROP_SATURATION = cv2.CAP_PROP_SATURATION  # Saturation of the image
CAP_PROP_HUE = cv2.CAP_PROP_HUE  # Hue of the image
CAP_PROP_GAIN = cv2.CAP_PROP_GAIN  # Gain of the image
CAP_PROP_EXPOSURE = cv2.CAP_PROP_EXPOSURE  # Exposure

# Color conversion codes
COLOR_BGR2GRAY = cv2.COLOR_BGR2GRAY  # Convert BGR to grayscale
COLOR_RGB2GRAY = cv2.COLOR_RGB2GRAY  # Convert RGB to grayscale
COLOR_GRAY2BGR = cv2.COLOR_GRAY2BGR  # Convert grayscale to BGR
COLOR_GRAY2RGB = cv2.COLOR_GRAY2RGB  # Convert grayscale to RGB
COLOR_BGR2RGB = cv2.COLOR_BGR2RGB  # Convert BGR to RGB
COLOR_RGB2BGR = cv2.COLOR_RGB2BGR  # Convert RGB to BGR

# Window properties
WINDOW_NORMAL = cv2.WINDOW_NORMAL  # The user can resize the window
WINDOW_AUTOSIZE = cv2.WINDOW_AUTOSIZE  # The window size is automatically adjusted to fit the displayed image
WINDOW_OPENGL = cv2.WINDOW_OPENGL  # Window with OpenGL support

# Mouse events
EVENT_MOUSEMOVE = cv2.EVENT_MOUSEMOVE  # Mouse movement
EVENT_LBUTTONDOWN = cv2.EVENT_LBUTTONDOWN  # Left button down
EVENT_RBUTTONDOWN = cv2.EVENT_RBUTTONDOWN  # Right button down
EVENT_MBUTTONDOWN = cv2.EVENT_MBUTTONDOWN  # Middle button down
EVENT_LBUTTONUP = cv2.EVENT_LBUTTONUP  # Left button up
EVENT_RBUTTONUP = cv2.EVENT_RBUTTONUP  # Right button up
EVENT_MBUTTONUP = cv2.EVENT_MBUTTONUP  # Middle button up
EVENT_LBUTTONDBLCLK = cv2.EVENT_LBUTTONDBLCLK  # Left button double click
EVENT_RBUTTONDBLCLK = cv2.EVENT_RBUTTONDBLCLK  # Right button double click
EVENT_MBUTTONDBLCLK = cv2.EVENT_MBUTTONDBLCLK  # Middle button double click

# Interpolation methods
INTER_NEAREST = cv2.INTER_NEAREST  # Nearest neighbor interpolation
INTER_LINEAR = cv2.INTER_LINEAR  # Bilinear interpolation
INTER_CUBIC = cv2.INTER_CUBIC  # Bicubic interpolation
INTER_AREA = cv2.INTER_AREA  # Area interpolation
INTER_LANCZOS4 = cv2.INTER_LANCZOS4  # Lanczos interpolation over 8x8 neighborhood

# Border types
BORDER_CONSTANT = cv2.BORDER_CONSTANT  # Border is filled with constant value
BORDER_REPLICATE = cv2.BORDER_REPLICATE  # Border replicates the border pixels
BORDER_REFLECT = cv2.BORDER_REFLECT  # Border reflects the border pixels
BORDER_WRAP = cv2.BORDER_WRAP  # Border is taken from the opposite edge
BORDER_REFLECT_101 = cv2.BORDER_REFLECT_101  # Border reflects the border pixels with a slight change
BORDER_TRANSPARENT = cv2.BORDER_TRANSPARENT  # Border is filled with transparent pixels
BORDER_DEFAULT = cv2.BORDER_DEFAULT  # Default border type
BORDER_ISOLATED = cv2.BORDER_ISOLATED  # Do not look outside the ROI

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
