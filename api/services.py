import io
import pyqrcode

def qr_code(source_string):
    code = pyqrcode.create(source_string)
    buf = io.BytesIO()
    code.png(buf, scale=5)
    buf.seek(0)
    image = buf.read()
    return image