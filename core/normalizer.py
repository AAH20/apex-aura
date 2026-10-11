"""
APEX_AURA Continuous Coordinate Normalizer.
Converts arbitrary display resolutions and Retina DPI scale factors into continuous [0.0, 1.0] affine coordinates.
"""

from typing import Tuple


class CoordinateNormalizer:
    def __init__(self, display_width: int = 1920, display_height: int = 1080, scale_factor: float = 1.0):
        self.width = display_width
        self.height = display_height
        self.scale_factor = scale_factor

    def normalize(self, x_pixel: float, y_pixel: float) -> Tuple[float, float]:
        norm_x = max(0.0, min(1.0, (x_pixel / self.scale_factor) / self.width))
        norm_y = max(0.0, min(1.0, (y_pixel / self.scale_factor) / self.height))
        return (round(norm_x, 6), round(norm_y, 6))

    def denormalize(self, norm_x: float, norm_y: float) -> Tuple[int, int]:
        x_pixel = int(norm_x * self.width * self.scale_factor)
        y_pixel = int(norm_y * self.height * self.scale_factor)
        return (x_pixel, y_pixel)
