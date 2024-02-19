
def convert_aspect_to_cardinal_direction(aspect: float):
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
        return None


nuts_lvl_3_encoding = {
    "AT111": 0,
    "AT112": 1,
    "AT113": 2,
    "AT121": 3,
    "AT122": 4,
    "AT123": 5,
    "AT124": 6,
    "AT125": 7,
    "AT126": 8,
    "AT127": 9,
    "AT130": 10,
    "AT211": 11,
    "AT212": 12,
    "AT213": 13,
    "AT221": 14,
    "AT222": 15,
    "AT223": 16,
    "AT224": 17,
    "AT225": 18,
    "AT226": 19,
    "AT311": 20,
    "AT312": 21,
    "AT313": 22,
    "AT314": 23,
    "AT315": 24,
    "AT321": 25,
    "AT322": 26,
    "AT323": 27,
    "AT331": 28,
    "AT332": 29,
    "AT333": 30,
    "AT334": 31,
    "AT335": 32,
    "AT341": 33,
    "AT342": 34
}


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


def apply_encoding(original_value: str, mapping: dict):
    """encodes nuts id to numerical id

    Args:
        original_value (str)
        mapping (dict): defines mapping between original value and encoded value
    """

    return mapping[original_value]
