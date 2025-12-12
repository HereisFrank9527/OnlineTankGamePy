"""
Collision detection and movement validation for server-side validation.
"""

from app.game.map import (
    MAP_BOUNDS,
    OBSTACLES,
    TANK_RADIUS,
)


def is_valid_position(x: float, y: float) -> bool:
    """
    Check if position is valid (within bounds and not in obstacle).
    
    Args:
        x: Position X coordinate
        y: Position Y coordinate
    
    Returns:
        True if position is valid for tank placement
    """
    bounds = MAP_BOUNDS
    if not (bounds.min_x <= x <= bounds.max_x):
        return False
    if not (bounds.min_y <= y <= bounds.max_y):
        return False

    for obstacle in OBSTACLES:
        if obstacle.intersects_circle(x, y, TANK_RADIUS):
            return False

    return True


def validate_movement(
    old_x: float, old_y: float, new_x: float, new_y: float
) -> bool:
    """
    Validate tank movement from one position to another.
    
    Args:
        old_x: Current X position
        old_y: Current Y position
        new_x: Desired X position
        new_y: Desired Y position
    
    Returns:
        True if movement is valid
    """
    if not is_valid_position(new_x, new_y):
        return False

    distance_x = new_x - old_x
    distance_y = new_y - old_y
    distance = (distance_x**2 + distance_y**2) ** 0.5

    max_step_distance = 50.0
    if distance > max_step_distance:
        return False

    return True


def is_valid_projectile(
    tank_x: float, tank_y: float, proj_x: float, proj_y: float
) -> bool:
    """
    Validate projectile origin is from tank position.
    
    Args:
        tank_x: Tank X position
        tank_y: Tank Y position
        proj_x: Projectile start X
        proj_y: Projectile start Y
    
    Returns:
        True if projectile originates from tank
    """
    distance_x = proj_x - tank_x
    distance_y = proj_y - tank_y
    distance = (distance_x**2 + distance_y**2) ** 0.5
    max_distance = TANK_RADIUS * 2
    return distance <= max_distance
