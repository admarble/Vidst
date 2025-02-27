"""Type stubs for OpenCV (cv2) functions used in the project."""


import numpy as np
import numpy.typing as npt

class VideoCapture:
    """Video capture interface."""

    def __init__(self, filename: str | int) -> None: ...
    def is_opened(self) -> bool: ...
    def read(self) -> tuple[bool, npt.NDArray[np.uint8]]: ...
    def get(self, prop_id: int) -> float: ...
    def set(self, prop_id: int, value: float) -> bool: ...
    def release(self) -> None: ...

def create_video_capture(source: str | int) -> VideoCapture: ...

# Video capture properties
CAP_PROP_POS_MSEC: int
CAP_PROP_POS_FRAMES: int
CAP_PROP_POS_AVI_RATIO: int
CAP_PROP_FRAME_WIDTH: int
CAP_PROP_FRAME_HEIGHT: int
CAP_PROP_FPS: int
CAP_PROP_FOURCC: int
CAP_PROP_FRAME_COUNT: int
CAP_PROP_FORMAT: int
CAP_PROP_MODE: int
CAP_PROP_BRIGHTNESS: int
CAP_PROP_CONTRAST: int
CAP_PROP_SATURATION: int
CAP_PROP_HUE: int
CAP_PROP_GAIN: int
CAP_PROP_EXPOSURE: int

# Color conversion codes
COLOR_BGR2GRAY: int
COLOR_RGB2GRAY: int
COLOR_GRAY2BGR: int
COLOR_GRAY2RGB: int
COLOR_BGR2RGB: int
COLOR_RGB2BGR: int

# Window properties
WINDOW_NORMAL: int
WINDOW_AUTOSIZE: int
WINDOW_OPENGL: int

# Mouse events
EVENT_MOUSEMOVE: int
EVENT_LBUTTONDOWN: int
EVENT_RBUTTONDOWN: int
EVENT_MBUTTONDOWN: int
EVENT_LBUTTONUP: int
EVENT_RBUTTONUP: int
EVENT_MBUTTONUP: int
EVENT_LBUTTONDBLCLK: int
EVENT_RBUTTONDBLCLK: int
EVENT_MBUTTONDBLCLK: int

# Interpolation methods
INTER_NEAREST: int
INTER_LINEAR: int
INTER_CUBIC: int
INTER_AREA: int
INTER_LANCZOS4: int

# Border types
BORDER_CONSTANT: int
BORDER_REPLICATE: int
BORDER_REFLECT: int
BORDER_WRAP: int
BORDER_REFLECT_101: int
BORDER_TRANSPARENT: int
BORDER_DEFAULT: int
BORDER_ISOLATED: int

__all__ = [
    "CAP_PROP_BRIGHTNESS",
    "CAP_PROP_CONTRAST",
    "CAP_PROP_EXPOSURE",
    "CAP_PROP_FORMAT",
    "CAP_PROP_FOURCC",
    "CAP_PROP_FPS",
    "CAP_PROP_FRAME_COUNT",
    "CAP_PROP_FRAME_HEIGHT",
    "CAP_PROP_FRAME_WIDTH",
    "CAP_PROP_GAIN",
    "CAP_PROP_HUE",
    "CAP_PROP_MODE",
    "CAP_PROP_POS_AVI_RATIO",
    "CAP_PROP_POS_FRAMES",
    "CAP_PROP_POS_MSEC",
    "CAP_PROP_SATURATION",
    "COLOR_BGR2GRAY",
    "COLOR_BGR2RGB",
    "COLOR_GRAY2BGR",
    "COLOR_GRAY2RGB",
    "COLOR_RGB2BGR",
    "COLOR_RGB2GRAY",
    "EVENT_LBUTTONDBLCLK",
    "EVENT_LBUTTONDOWN",
    "EVENT_LBUTTONUP",
    "EVENT_MBUTTONDBLCLK",
    "EVENT_MBUTTONDOWN",
    "EVENT_MBUTTONUP",
    "EVENT_MOUSEMOVE",
    "EVENT_RBUTTONDBLCLK",
    "EVENT_RBUTTONDOWN",
    "EVENT_RBUTTONUP",
    "INTER_AREA",
    "INTER_CUBIC",
    "INTER_LANCZOS4",
    "INTER_LINEAR",
    "INTER_NEAREST",
    "WINDOW_AUTOSIZE",
    "WINDOW_NORMAL",
    "WINDOW_OPENGL",
    "BORDER_CONSTANT",
    "BORDER_DEFAULT",
    "BORDER_ISOLATED",
    "BORDER_REFLECT",
    "BORDER_REFLECT_101",
    "BORDER_REPLICATE",
    "BORDER_TRANSPARENT",
    "BORDER_WRAP",
    "VideoCapture",
    "create_video_capture",
]
