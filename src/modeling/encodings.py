
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
    else:
        return -1
    

def convert_slope_to_classes(slope: float) -> int:
    """categorization of slope into classes after Müller & Vacik (2020)

    Args:
        slope (float): inclination in ° (ranges from 0-90)

    Returns:
        int: slope encoded
    """

    if (slope < 10):
        return 0
    elif (slope >= 10) & (slope < 20):
        return 1
    elif (slope >= 20) & (slope < 30):
        return 2
    elif (slope >= 30) & (slope < 40):
        return 3
    elif (slope >= 40):
        return 4
    else: 
        return -1
    

def convert_elevation_to_classes(elevation: float) -> int:
    """categorization of elevation into classes after Müller & Vacik (2020)

    Args:
        elevation (float): elevation in meter a.s.l

    Returns:
        int: elevation encoded
    """

    if (elevation < 500):
        return 0
    elif (elevation >= 500) & (elevation < 800):
        return 1
    elif (elevation >= 800) & (elevation < 1500):
        return 2
    elif (elevation >= 1500) & (elevation < 1800):
        return 3
    elif (elevation >= 1800) & (elevation < 2200):
        return 4
    elif (elevation >= 2200):
        return 5
    else:
        return -1


def convert_population_to_classes(population: float) -> int:
    """categorization of population into classes after www.statistik.at

    Args:
        population (float): population density (nr of people per km2)

    Returns:
        int: population encoded
    """

    if (population == 0):
        return 0
    elif (population > 0) & (population <= 50):
        return 1
    elif (population > 50) & (population <= 100):
        return 2
    elif (population > 100) & (population <= 500):
        return 3
    elif (population > 500) & (population <= 1000):
        return 4
    elif (population > 1000):
        return 5
    else: 
        return -1


def apply_encoding(original_value: str, mapping: dict):
    """encodes nuts id to numerical id

    Args:
        original_value (str)
        mapping (dict): defines mapping between original value and encoded value
    """

    return mapping[original_value]

def map_to_binary(x):
    return 1 if x > 0 else 0


naturraumregionen_encoding = {
    "Pannonische Flach- und Hügelländer": 0,
    "Südöstliches Alpenvorland": 1,
    "Nördliches Granit- und Gneishochland": 2,
    "Nördliches Alpenvorland": 3,
    "Östliche Nordalpen": 4,
    "Zentralalpen - südöstlicher Teil": 5,
    "Klagenfurter Becken": 6,
    "Südalpen": 7,
    "Zentralalpen - zentraler Teil": 8,
    "Mittlere und westliche Nordalpen": 9
}
