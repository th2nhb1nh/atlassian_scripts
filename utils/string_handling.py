import base64

def encode_base64(str):
    return base64.b64encode(str.encode('utf-8')).decode('utf-8')
