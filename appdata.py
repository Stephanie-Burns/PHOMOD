
import random
import base64
import zlib


SYS_LOCALE_DATA = (
    b"eJxdU0uWozAM3HMKr2YVbpEFmzy4gsACPG0knj+Zpk8/ZUN60rPyT59SVXk40qpi"
    b"OhLrOZo+B/Po77EZNLEkR94fpmO/z9nfTD8+neaIK8S0gT0lts0QdKSxxJGf237n"
    b"QMmpkDcPtaYP08ox4U6D+WXuPOZl4dAMFCIadkw72s5X16ATx+hkMZ1DHeQe749J"
    b"2+5AA3RJbnNfbK8eCwlOAeV9/uRm4DDzlCqmfaUvChb7V9iVlNOek7m7gEgNRzN4"
    b"psg3pDzZ9MKICtg8OUy67d5NZVp0iG6RAp9Ew4YpO8pSXkqk12CNzqVB9hRMvzkB"
    b"Y+auf8QrWUxBTkBmhTZ9HDWLZXHCWP8f550v1t0zktKJqYjwalKP7YnsFGQuLFYN"
    b"OresbT8lqgN9F68SofrTTVy1qJxXMQC/H0U/i9QlxZanHktyEKxA2lksy4RjMwA4"
    b"7RWZel0CbVBTzAOD+UrWR9L9orYa6XZ6TG28CCP7rUEt+GaBLBacnPbA3VFy4aSF"
    b"K6XvSf/0Pr2KCX7jAvhJEG8LpjtvcDmcHVPbZezNT6/G9MMjGNNN5bFUjy6W/wD6"
    b"N2xCfMUVmI9TxJWyByoSqFU/yV+n2jfa"
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
