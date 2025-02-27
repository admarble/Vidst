"""Type stubs for OpenCV-Python."""

from typing import Any, Tuple, Union
import numpy as np

class VideoCapture:
    def __init__(self, filename: str) -> None: ...
    def isOpened(self) -> bool: ...
    def read(self) -> Tuple[bool, np.ndarray]: ...
    def get(self, propId: int) -> float: ...
    def set(self, propId: int, value: float) -> bool: ...
    def release(self) -> None: ...

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
CAP_PROP_CONVERT_RGB: int
CAP_PROP_WHITE_BALANCE_BLUE_U: int
CAP_PROP_RECTIFICATION: int
CAP_PROP_MONOCHROME: int
CAP_PROP_SHARPNESS: int
CAP_PROP_AUTO_EXPOSURE: int
CAP_PROP_GAMMA: int
CAP_PROP_TEMPERATURE: int
CAP_PROP_TRIGGER: int
CAP_PROP_TRIGGER_DELAY: int
CAP_PROP_WHITE_BALANCE_RED_V: int
CAP_PROP_ZOOM: int
CAP_PROP_FOCUS: int
CAP_PROP_GUID: int
CAP_PROP_ISO_SPEED: int
CAP_PROP_BACKLIGHT: int
CAP_PROP_PAN: int
CAP_PROP_TILT: int
CAP_PROP_ROLL: int
CAP_PROP_IRIS: int
CAP_PROP_SETTINGS: int
CAP_PROP_BUFFERSIZE: int
CAP_PROP_AUTOFOCUS: int

class error(Exception): ...

def imread(filename: str, flags: int = ...) -> np.ndarray: ...
def imwrite(filename: str, img: np.ndarray, params: Any = ...) -> bool: ...
def imshow(winname: str, mat: np.ndarray) -> None: ...
def waitKey(delay: int = ...) -> int: ...
def destroyAllWindows() -> None: ...
def destroyWindow(winname: str) -> None: ...
