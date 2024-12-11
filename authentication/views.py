from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from django.contrib.auth import get_user_model
from django.contrib.auth import login, authenticate, logout
from store.models import Product, Order, Genre
from django.contrib.auth.decorators import login_required
from store.models import Cart
from django.db.models import Count
from payment.models import UserCard

User = get_user_model()


def register_view(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        email_error = ''
        password_error = ''
        error_password = ''

        errors = 0

        email = User.objects.filter(email=email).first()
        if email:
            email_error = 'This email is already registered.'
            errors += 1

        if password != confirm_password:
            password_error = 'Passwords do not match.'
            errors += 1

        if not any(char.isdigit() for char in password):
            error_password = 'Password must include at least one number. (0-9) or one special character.'
            errors += 1

        if errors >= 1:
            d = {
                'email_error': email_error,
                'password_error': password_error,
                'error_password': error_password
            }
            return render(request, 'register.html', d)
        else:
            print('+' * 80)
            print(email)
            print('+' * 80)
            user = User(
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name'],
                email=request.POST['email'],
            )
            user.set_password(password)
            user.save()

            login(request, user)
            return redirect('/profile')
    return render(request, 'register.html')


def login_view(request):
    user = request.user
    if user.is_authenticated:
        return redirect('/profile')
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        if not email or not password:
            return HttpResponseBadRequest('Please enter all the fields')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('/profile')
        else:
            return HttpResponseBadRequest('Invalid email or password')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('/login')


@login_required(login_url='/login')
def profile_view(request):
    user = request.user
    liked_products = Product.objects.filter(like__user=request.user)
    cart_counter = Cart.objects.filter(user=request.user, ordered=False).aggregate(Count('user'))
    credit_card = UserCard.objects.filter(user_id=request.user.id).first()
    genre_for_base = Genre.objects.all().order_by('-created_at')[:5]
    if credit_card is not None:
        card_num = str(credit_card.pan)[-4:]
    else:
        card_num = 0
    orders = Order.objects.filter(user__first_name=user.first_name, user__last_name=user.last_name).order_by(
        '-created_at')
    return render(request, 'profile.html',
                  {'liked_products': liked_products, 'cart_num': cart_counter['user__count'], 'user': request.user,
                   'GENDER_CHOICE': request.user._meta.get_field('gender').choices, 'card_num': card_num,
                   'credit_card': credit_card, 'orders': orders, 'genre_for_base': genre_for_base})


@login_required(login_url='/login')
def edit_profile_view(request):
    user = request.user
    genre_for_base = Genre.objects.all().order_by('-created_at')[:5]
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.gender = request.POST.get('gender', user.gender)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.save()
        return redirect('profile')
    return render(request, 'profile.html', {'user': user, 'genre_for_base': genre_for_base})


@login_required(login_url='/login')
def edit_profile_image_view(request):
    if request.method == 'POST':
        user = request.user
        if 'profile_image' in request.FILES:
            user.image = request.FILES['profile_image']
            user.save()
        return redirect('profile')


@login_required(login_url='/login')
def exit_card_view(request, pk):
    card = UserCard.objects.filter(id=pk).first()
    if card:
        card.delete()
    return redirect('/profile')
