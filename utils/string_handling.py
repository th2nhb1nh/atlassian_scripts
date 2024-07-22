# utils/string_handling.py
import base64

def encode_base64(str):
    return base64.b64encode(str.encode('utf-8')).decode('utf-8')

def get_initials(string):
    words = string.split()
    initials = ''.join(word[0].upper() for word in words[:3])
    return initials
