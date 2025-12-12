"""
Game map configuration with boundaries, obstacles, and spawn points.

Map Layout:
- Bounds: 0,0 to 800,600 pixels
- Tank radius: 15 pixels (for collision)
- Obstacles: Fixed rectangular barriers
- Power-ups: Health and weapon upgrades
- Spawn points: 8 fixed locations for players
"""

from dataclasses import dataclass


@dataclass
class Bounds:
    """Map boundaries."""

    min_x: float = 0.0
    min_y: float = 0.0
    max_x: float = 800.0
    max_y: float = 600.0


@dataclass
class Rect:
    """Rectangle for obstacles and collision detection."""

    x: float
    y: float
    width: float
    height: float

    def contains_point(self, px: float, py: float) -> bool:
        """Check if point is inside rectangle."""
        return (
            self.x <= px <= self.x + self.width
            and self.y <= py <= self.y + self.height
        )

    def intersects_circle(self, cx: float, cy: float, radius: float) -> bool:
        """Check if circle intersects with rectangle."""
        closest_x = max(self.x, min(cx, self.x + self.width))
        closest_y = max(self.y, min(cy, self.y + self.height))
        distance_x = cx - closest_x
        distance_y = cy - closest_y
        return (distance_x * distance_x + distance_y * distance_y) <= (
            radius * radius
        )


TANK_RADIUS = 15.0
MAP_BOUNDS = Bounds()

OBSTACLES = [
    Rect(100, 100, 100, 50),
    Rect(600, 100, 100, 50),
    Rect(200, 300, 400, 50),
    Rect(100, 450, 100, 50),
    Rect(600, 450, 100, 50),
    Rect(350, 200, 100, 80),
    Rect(350, 400, 100, 80),
]

SPAWN_POINTS = [
    (50.0, 50.0),
    (750.0, 50.0),
    (50.0, 550.0),
    (750.0, 550.0),
    (400.0, 50.0),
    (400.0, 550.0),
    (50.0, 300.0),
    (750.0, 300.0),
]

POWER_UP_LOCATIONS = [
    (200.0, 150.0),
    (600.0, 150.0),
    (200.0, 450.0),
    (600.0, 450.0),
]
