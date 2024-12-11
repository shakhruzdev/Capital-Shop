from django.core.exceptions import ValidationError


def validate_uz_phone_number(phone_number):
    phone_number = phone_number.replace(' ', '')
    if len(phone_number) != 13:
        raise ValidationError('The phone number must be 13 digits')
    if not phone_number.startswith('+998'):
        raise ValidationError('The phone number must start with +998')
    if not phone_number[1:].isdigit():
        raise ValidationError('The phone number must only contain digits (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)')
