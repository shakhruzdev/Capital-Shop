import qrcode
import json
from io import BytesIO
from django.core.files.base import ContentFile


def generate_qr_code(order):
    qr_data = {
        "order_id": order.id,
        "uuid": str(order.uuid)
    }

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(json.dumps(qr_data))
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)

    order.qr_code.save(f"order_{order.id}_qr.png", ContentFile(buffer.read()), save=False)
    buffer.close()
    order.save()
