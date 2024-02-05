
def convert_aspect_to_cardinal_direction(aspect: float) -> int:
    """converts aspect degree values to cardinal direction classes

    Args:
        aspect (float): value between 0 and 360, indicating exposition of slope

    Returns:
        (int): cardinal direction class
    """
    if (aspect >= 337.5) | (aspect < 22.5):
        return 0  # N
    elif (aspect >= 22.5) & (aspect < 67.5):
        return 1  # NE
    elif (aspect >= 67.5) & (aspect < 112.5):
        return 2  # E
    elif (aspect >= 112.5) & (aspect < 157.5):
        return 3  # SE
    elif (aspect >= 157.5) & (aspect < 202.5):
        return 4  # S
    elif (aspect >= 202.5) & (aspect < 247.5):
        return 5  # SW
    elif (aspect >= 247.5) & (aspect < 292.5):
        return 6  # W
    elif (aspect >= 292.5) & (aspect < 337.5):
        return 7  # NW
