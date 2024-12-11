from django.shortcuts import render, redirect
from .models import Contact
import requests
from store.models import Cart, Genre
from django.db.models import Count
from django.contrib.auth.decorators import login_required


@login_required(login_url='/login')
def contact_view(request):
    first_name = request.user.first_name
    email = request.user.email
    cart_counter = Cart.objects.filter(user=request.user, ordered=False).aggregate(Count('user'))
    genre_for_base = Genre.objects.all().order_by('-created_at')[:5]
    if request.method == 'POST':
        data = request.POST
        obj = Contact.objects.create(name=first_name, email=email, phone=data['phone_number'],
                                     message=data['message'])
        obj.save()

        token = '7755732315:AAEzxJ7LF49kScC7HpmxLEaBeZHehV8WeSU'
        chat_id = '5467422443'

        requests.get(
            f"""https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text=\nname: {obj.name}\nemail: {obj.email}\nphone: {obj.phone}\nmessage: {obj.message}""")

        return redirect('/contact')
    context = {
        'cart_num': cart_counter['user__count'],
        'genre_for_base': genre_for_base,
    }
    return render(request, 'contact.html', context)
