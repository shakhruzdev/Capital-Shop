import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse


def validate_qr_code(request):
    from store.models import Order
    qr_data = request.POST.get('qr_data')
    decoded_data = json.loads(qr_data)

    order_id = decoded_data.get('order_id')
    uuid = decoded_data.get('uuid')

    order = get_object_or_404(Order, id=order_id, uuid=uuid)

    if order:
        return JsonResponse({
            'status': 'success',
            'order_id': order.id,
            'uuid': order.uuid,
            'message': 'QR code is valid.'
        })
    else:
        return JsonResponse({
            'status': 'failure',
            'message': 'Invalid QR code.'
        })
