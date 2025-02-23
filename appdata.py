
import random
import base64
import zlib


SYS_LOCALE_DATA = (
    b"eJxtVDuW2zAM7H0Kpkll7xXSuFCzT74CRMEyY5rU48e7yukzAGWvnGwlisRnMBjg"
    b"tJRLDKajMHrOpq/JvPfH/GN3+v7hl+kv5siU3t7edqdYOBRH3i+mYz+fq9+bfri7"
    b"WDOuYH9I7KnwuDulONAgduTPh37mRMXFQN68x9H0yV44F9zFZH4i/lCnidPuRCkj"
    b"ecc0A8JZEUgoyzm7MJnOIQ58F32MY/WUTD+vkY88cxg5WMfqVeKhW5D5IBY394fH"
    b"NflEAX8JDr5+8u7E6cy2KNj5Qn8ojTg/zFanWuZazNElWMa07E6eKfMeLnc2fWBY"
    b"JRzunGy8zd5ZoQEZspuC1EUhphtAdlSDvIilj2k0cVPJzQVQaY7xI/hII6ogF8Cy"
    b"QrPXRb04TC4wvv+WsyWS4+wZTqVhku48kujvoSFrnToLvUph56bLobeFtKBncO0d"
    b"ot+dZW2SNkO7BPj9EOKnaEBcRnnq8SnogkLaNgXAaVZk0ccp0Q1tDuYdhXkl61ri"
    b"vFKrCts3IcYxr4TR+OzB2uWnNmoYwUnTDe4W8YXEJlZKt05f/W4iRgW/cQH8FGA/"
    b"CqYj3zAKkHwuh67ibF5FnMuLRlCms/Io9BRp1y0XTkAznGtuYpAyy0V1J7HzttBn"
    b"KLX6CK+A17FoMLa6BP9imq8A6kG5bbOpGpaywcBQU9bSRlbjta5taqGY7AXNyV84"
    b"jlToq9fxY8X+IjmRaijfdkFk7XKhK+dtWviAKLIql47SACdEFWtCBJkl3BWdZiyI"
    b"unLqCRRq/G/WSZPckJuKhQ7M1XYIJGp7vrNMwqPLQ46eMSH/cv2fnED0Xod8M//P"
    b"BRdTcnJ4bpm9OAhCfpVIvc2iiUeKvc60Hl7WhmR/GVZa/h+ktX3ky5cusyQOV17a"
    b"sGDlCBczFXsRHeeKaetcY6sWGNNVz4+tw9YJgYge5+ysUif1n51tO/+dfXlMh0gO"
    b"W817xtbgmtBrZx8ctH1xjqkVwhuMzy2F1CqHtnfYe2V6Fb8up79KHmlk"
)

def _decode_phomod():
    """ Decodes the PHOMOD list. """
    decoded = base64.b64decode(SYS_LOCALE_DATA)
    decompressed = zlib.decompress(decoded).decode('utf-8')
    return decompressed.split('\n')

def phomod_map():
    """ Returns a PHOMOD. """
    acronyms = _decode_phomod()
    return random.choice(acronyms)
