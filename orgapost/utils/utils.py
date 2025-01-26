def remove_non_bmp_characters(text):
    """
    Supprime les caractères Unicode non pris en charge par ChromeDriver (hors BMP).
    """
    return ''.join(c for c in text if ord(c) <= 0xFFFF)