from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Card, UserCard
from store.models import Order
from .utils import generate_qr_code
from django.urls import reverse


@login_required(login_url='login')
def pay_online_view(request, pk):
    if request.method == 'POST':
        data = request.POST
        check = 0

        pan_not_found_error = ''
        pan_len_error = ''
        expired_month_error = ''
        expired_year_error = ''
        cvv_error = ''
        expired_month_not_match_error = ''

        pan = Card.objects.filter(pan=data.get('card_number')).first()

        if pan is None:
            pan_not_found_error = 'Card not found'
            check += 1

        if pan is not None and int(data.get('expire_month')) > 12:
            expired_month_error = 'it must be exist month: 1 to 12'
            check += 1

        if pan is not None and int(data.get('expire_month')) != pan.expired_month:
            expired_month_not_match_error = 'Month is not match'
            check += 1

        created_year = Card.objects.filter(pan=data.get('card_number')).first()

        if pan is not None and int(data.get('expire_year')) > created_year.expired_year:
            expired_year_error = 'The card has expired'
            check += 1

        cvv = Card.objects.filter(cvv=data.get('cvv')).first()
        if pan is not None and cvv is None:
            cvv_error = "Card's cvv is incorrect "
            check += 1

        if check >= 1:
            d = {
                'pan_not_found_error': pan_not_found_error,
                'order_id': pk,
                'pan_len_error': pan_len_error,
                'expired_month_error': expired_month_error,
                'expired_year_error': expired_year_error,
                'cvv_error': cvv_error,
                'expired_month_not_match_error': expired_month_not_match_error
            }
            return render(request, 'payment-d.html', context=d)
        else:
            user_card = UserCard.objects.filter(user_id=request.user.id, pan=data.get('card_number'),
                                                expired_month=data.get('expire_month'),
                                                expired_year=data.get('expire_year'), cvv=data.get('cvv')).first()
            if user_card:
                order_payed = Order.objects.filter(id=pk, user=request.user).first()
                user_card.balance -= order_payed.total_price
                order_payed.payment_status = 2
                order_payed.save()
                user_card.save()
                card = Card.objects.filter(pan=data.get('card_number'),
                                           expired_month=data.get('expire_month'),
                                           expired_year=data.get('expire_year'), cvv=data.get('cvv')).first()
                card.balance = user_card.balance
                card.save()
                generate_qr_code(order_payed)
                return redirect(reverse('profile'))
            else:
                card = Card.objects.filter(pan=data.get('card_number'),
                                           expired_month=data.get('expire_month'),
                                           expired_year=data.get('expire_year'), cvv=data.get('cvv')).first()
                order_payed = Order.objects.filter(id=pk, user=request.user).first()
                user_card.balance -= order_payed.total_price
                order_payed.payment_status = 2
                order_payed.save()
                user_card.save()
                card.save()
                generate_qr_code(order_payed)
                return redirect(reverse('profile'))
    return render(request, 'payment-d.html', {'order_id': pk})


def add_card(request):
    return render(request, 'add_card.html')


def add_card_details_view(request):
    if request.method == 'POST':
        data = request.POST
        check = 0

        pan_not_found_error = ''
        pan_len_error = ''
        expired_month_error = ''
        expired_year_error = ''
        cvv_error = ''
        expired_month_not_match_error = ''

        pan = Card.objects.filter(pan=data.get('card_number')).first()

        if pan is None:
            pan_not_found_error = 'Card not found'
            check += 1

        if pan is not None and int(data.get('expire_month')) > 12:
            expired_month_error = 'it must be exist month: 1 to 12'
            check += 1

        if pan is not None and int(data.get('expire_month')) != pan.expired_month:
            expired_month_not_match_error = 'Month is not match'
            check += 1

        created_year = Card.objects.filter(pan=data.get('card_number')).first()

        if pan is not None and int(data.get('expire_year')) > created_year.expired_year:
            expired_year_error = 'The card has expired'
            check += 1

        cvv = Card.objects.filter(cvv=data.get('cvv')).first()
        if pan is not None and cvv is None:
            cvv_error = "Card's cvv is incorrect "
            check += 1

        if check >= 1:
            d = {
                'pan_not_found_error': pan_not_found_error,
                'pan_len_error': pan_len_error,
                'expired_month_error': expired_month_error,
                'expired_year_error': expired_year_error,
                'cvv_error': cvv_error,
                'expired_month_not_match_error': expired_month_not_match_error
            }
            return render(request, 'add_card.html', context=d)
        else:
            custom_card = Card.objects.filter(pan=data.get('card_number'), expired_month=data.get('expire_month'),
                                              expired_year=data.get('expire_year'), cvv=data.get('cvv')).first()
            user_card = UserCard.objects.create(user_id=request.user.id, first_name=custom_card.first_name,
                                                last_name=custom_card.last_name,
                                                pan=custom_card.pan, cvv=custom_card.cvv,
                                                bank_name=custom_card.bank_name,
                                                card_name=custom_card.card_name, phone_number=custom_card.phone_number,
                                                balance=custom_card.balance, created_month=custom_card.created_month,
                                                created_year=custom_card.created_year,
                                                expired_month=custom_card.expired_month,
                                                expired_year=custom_card.expired_year)
            user_card.save()
    return redirect(reverse('profile'))
