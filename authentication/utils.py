from django.core.exceptions import ValidationError


def validate_uz_phone_number(phone_number):
    if len(phone_number) != 13:
        raise ValidationError('Length of phone number must be 13')
    if phone_number[:4] != '+998':
        raise ValidationError('Phone number must start with +998')
    if not phone_number[1:13].isdigit():
        raise ValidationError('Phone number must be digit')
