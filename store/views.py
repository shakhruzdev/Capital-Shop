import json
from django.http import JsonResponse
from .models import CATEGORY_CHOICES
from store.models import Comment, Brand
from django.db.models import Count, Sum
from decimal import Decimal, ROUND_DOWN
from django.http.response import HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Size, Color, Genre, Cart, Like, Order, Promocode, PromoCodeObj
from django.urls import reverse
from payment.utils import generate_qr_code
from django.core.paginator import Paginator
from django.db.models import Count

CATEGORY = {name: value for value, name in CATEGORY_CHOICES}


@login_required(login_url='/login')
def categories_view(request):
    category_value = CATEGORY.get(request.GET.get('category', '').upper())
    products = Product.objects.filter(category=category_value)

    cart_counter = Cart.objects.filter(user=request.user, ordered=False).aggregate(Count('user'))
    cart_items = Cart.objects.filter(user=request.user, ordered=False).values_list('product_id', flat=True)
    liked_products = Like.objects.filter(user=request.user).values_list('product_id', flat=True)
    genre_for_base = Genre.objects.all().order_by('-created_at')[:5]

    sizes = Size.objects.all()
    colors = Color.objects.all()
    genres = Genre.objects.all()
    brands = Brand.objects.all()

    if request.method == 'POST':
        size = request.POST.get('size')
        color = request.POST.get('color')
        genre = request.POST.getlist('genres')
        brand = request.POST.getlist('brands')
        from_amount = request.POST.get('from_amount')
        to_amount = request.POST.get('to_amount')

        if size:
            products = products.filter(size__name=size)

        if color:
            products = products.filter(color__name=color)

        if genre:
            products = products.filter(genre__name__in=genre)

        if brand:
            products = products.filter(brand__name__in=brand)

        if from_amount or to_amount:
            products = products.filter(price_with_discount__gte=from_amount, price_with_discount__lte=to_amount)

    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        'products': page,
        'cart_items': cart_items,
        'liked_products': liked_products,
        'sizes': sizes,
        'colors': colors,
        'genres': genres,
        'brands': brands,
        'cart_num': cart_counter['user__count'],
        'genre_for_base': genre_for_base,
    }
    return render(request, 'categories.html', context)


@login_required(login_url='/login')
def product_detail_view(request, pk):
    product = get_object_or_404(Product, id=pk)
    comments = Comment.objects.filter(product=product)
    rated_product = Comment.objects.filter(user=request.user).values_list('product_id', flat=True)
    total_rating = sum(comment.rating for comment in comments)
    rating_count = comments.count()
    average_rating = total_rating / rating_count if rating_count > 0 else 0
    cart_counter = Cart.objects.filter(user=request.user, ordered=False).aggregate(Count('user'))
    liked_products = Like.objects.filter(user=request.user).values_list('product_id', flat=True)
    genre_for_base = Genre.objects.all().order_by('-created_at')[:5]

    full_stars = int(product.rating)
    has_half_star = (product.rating - full_stars) >= 0.5
    empty_stars = 5 - full_stars - int(has_half_star)

    full_star_html = '<i class="fas fa-star"></i>' * full_stars
    partial_star_html = '<i class="fas fa-star-half"></i>' if has_half_star else ''
    empty_star_html = '<i class="far fa-star"></i>' * empty_stars

    comment_order = Order.objects.filter(user=request.user, product__id=pk, status=3).exists()
    commented = Comment.objects.filter(user=request.user, product__id=pk).exists()

    if request.method == 'POST':
        if comment_order and not commented:
            rating = request.POST.get('rating')
            comment_message = request.POST.get('comment')

            if rating and comment_message:
                Comment.objects.create(
                    user=request.user,
                    product=product,
                    message=comment_message,
                    rating=int(rating),
                )

                product.rating_count += 1
                total_ratings = product.rating * (product.rating_count - 1) + int(rating)
                product.rating = total_ratings / product.rating_count
                product.save()

                return redirect(reverse('product_detail', args=[pk]))

    return render(request, 'pro-details.html', {
        'product': product,
        'comments': comments,
        'average_rating': average_rating,
        'rated_product': rated_product,
        'full_star_html': full_star_html,
        'partial_star_html': partial_star_html,
        'empty_star_html': empty_star_html,
        'cart_num': cart_counter['user__count'],
        'liked_products': liked_products,
        'genre_for_base': genre_for_base,
        'comment_order': comment_order,
        'commented': commented
    })


@login_required(login_url='/login')
def cart_view(request):
    cart = Cart.objects.filter(user=request.user, ordered=False)
    cart_counter = Cart.objects.filter(user=request.user, ordered=False).aggregate(Count('user'))
    subtotal = cart.aggregate(Sum('total_price_with_discount'))['total_price_with_discount__sum'] or 0
    card_objs = Cart.objects.filter(user=request.user, ordered=False)
    total_quantity = Cart.objects.filter(
        user=request.user, ordered=False).aggregate(Sum('quantity'))['quantity__sum'] or 0
    with_discount = Cart.objects.filter(user=request.user, ordered=False).aggregate(
        Sum('total_price_with_discount'))['total_price_with_discount__sum'] or 0

    without_discount = Cart.objects.filter(user=request.user, ordered=False).aggregate(
        Sum('total_price_without_discount'))['total_price_without_discount__sum'] or 0

    genre_for_base = Genre.objects.all().order_by('-created_at')[:5]
    saving = without_discount - with_discount
    context = {
        "cart": cart,
        "cart_num": cart_counter['user__count'],
        "subtotal": subtotal,
        "card_objs": card_objs,
        "total_quantity": total_quantity,
        "with_discount": Decimal(with_discount).quantize(Decimal('0.01'), rounding=ROUND_DOWN),
        "without_discount": Decimal(without_discount).quantize(Decimal('0.01'), rounding=ROUND_DOWN),
        "saving": Decimal(saving).quantize(Decimal('0.01'), rounding=ROUND_DOWN),
        'genre_for_base': genre_for_base
    }
    return render(request, 'cart.html', context)


@login_required(login_url='/login')
def add_to_cart(request, pk):
    referer = request.META.get('HTTP_REFERER')
    product_id = get_object_or_404(Product, id=pk)
    cart = Cart.objects.filter(user=request.user, ordered=False, product=product_id).first()
    if not cart:
        cart = Cart.objects.create(user=request.user, product=product_id, name=product_id.name, price=product_id.price,
                                   discount=product_id.discount, price_with_discount=product_id.price_with_discount,
                                   total_price_with_discount=product_id.price_with_discount,
                                   total_price_without_discount=product_id.price)
        cart.quantity += 1
        cart.product.product_quantity -= 1
        cart.product.save()
        cart.save()
    else:
        cart.quantity += 1
        cart.product.product_quantity += 1
        cart.product.save()
        cart.total_price_with_discount += product_id.price_with_discount
        cart.total_price_without_discount = float(cart.total_price_without_discount) + product_id.price
        cart.save()

    if referer == 'http://127.0.0.1:8000/categories/?category=Men':
        return redirect('cart')
    elif referer == 'http://127.0.0.1:8000/categories/?category=Women':
        return redirect('cart')
    elif referer == 'http://127.0.0.1:8000/categories/?category=Baby':
        return redirect('/cart')
    elif referer == f'http://127.0.0.1:8000/products/{pk}':
        return redirect('/cart')
    else:
        return redirect('/cart')


@login_required(login_url='/login')
def like_view(request, pk):
    product = get_object_or_404(Product, id=pk)
    like, created = Like.objects.get_or_create(user=request.user, product=product)
    if not created:
        like.delete()
    return redirect('/profile')


@login_required(login_url='/auth/login')
def checkout_view(requests):
    if requests.method == 'POST':
        user = requests.user
        message = ''
        data = requests.POST
        promo = Promocode.objects.filter(name=data.get('promo_code')).first()
        used_promo = PromoCodeObj.objects.filter(promo__name=data.get('promo_code'), user=user).first()

        if data.get('promo_code') != '' and promo is None:
            card_objs = Cart.objects.filter(user__first_name=user.first_name, user__last_name=user.last_name,
                                            ordered=False)
            cart_counter = Cart.objects.filter(user=user, ordered=False).aggregate(Count('user'))
            genre_for_base = Genre.objects.all().order_by('-created_at')[:5]

            promo_not_exist_error = ''

            total_quantity = 0
            with_discount = 0
            without_discount = 0

            if card_objs:
                total_quantity = Cart.objects.filter(user=user, ordered=False).aggregate(Sum('quantity'))[
                                     'quantity__sum'] or 0

                with_discount = Cart.objects.filter(user=user, ordered=False).aggregate(
                    Sum('total_price_with_discount'))['total_price_with_discount__sum'] or 0

                without_discount = Cart.objects.filter(user=user, ordered=False).aggregate(
                    Sum('total_price_without_discount'))['total_price_without_discount__sum'] or 0

                promo_not_exist_error = 'Promocode does not exists'

            d = {
                'cart_num': cart_counter['user__count'],
                'total_quantity': total_quantity,
                'with_discount': with_discount,
                'without_discount': without_discount,
                'promo_not_exist_error': promo_not_exist_error,
                'genre_for_base': genre_for_base
            }
            return render(requests, 'checkout.html', d)
        elif data.get('promo_code') != '' and used_promo:
            card_objs = Cart.objects.filter(user__first_name=user.first_name, user__last_name=user.last_name,
                                            ordered=False)
            cart_counter = Cart.objects.filter(user=user, ordered=False).aggregate(Count('user'))
            genre_for_base = Genre.objects.all().order_by('-created_at')[:5]

            promo_used_error = ''

            total_quantity = 0
            with_discount = 0
            without_discount = 0

            if card_objs:
                total_quantity = Cart.objects.filter(user=user, ordered=False).aggregate(Sum('quantity'))[
                                     'quantity__sum'] or 0

                with_discount = Cart.objects.filter(user=user, ordered=False).aggregate(
                    Sum('total_price_with_discount'))['total_price_with_discount__sum'] or 0

                without_discount = Cart.objects.filter(user=user, ordered=False).aggregate(
                    Sum('total_price_without_discount'))['total_price_without_discount__sum'] or 0

                promo_used_error = 'Promocode already used'

            d = {
                'cart_num': cart_counter['user__count'],
                'total_quantity': total_quantity,
                'with_discount': with_discount,
                'without_discount': without_discount,
                'promo_used_error': promo_used_error,
                'genre_for_base': genre_for_base
            }
            return render(requests, 'checkout.html', d)

        if data.get('delivery') == 'courier' and data.get('delivery_point') == '':
            card_objs = Cart.objects.filter(user__first_name=user.first_name, user__last_name=user.last_name,
                                            ordered=False)
            cart_counter = Cart.objects.filter(user=user, ordered=False).aggregate(Count('user'))
            genre_for_base = Genre.objects.all().order_by('-created_at')[:5]

            total_quantity = 0
            with_discount = 0
            without_discount = 0

            if card_objs:
                total_quantity = Cart.objects.filter(user=user, ordered=False).aggregate(Sum('quantity'))[
                                     'quantity__sum'] or 0

                with_discount = Cart.objects.filter(user=user, ordered=False).aggregate(
                    Sum('total_price_with_discount'))['total_price_with_discount__sum'] or 0

                without_discount = Cart.objects.filter(user=user, ordered=False).aggregate(
                    Sum('total_price_without_discount'))['total_price_without_discount__sum'] or 0

                message = 'this field required'

            d = {
                'cart_num': cart_counter['user__count'],
                'total_quantity': total_quantity,
                'with_discount': with_discount,
                'without_discount': without_discount,
                'message': message,
                'genre_for_base': genre_for_base
            }
            return render(requests, 'checkout.html', context=d)

        if data.get('payment') == 'online':
            if data.get('delivery') == 'pickup':
                delivery = 1
            else:
                delivery = 2
            if data.get('payment') == 'byhand':
                payment = 1
            else:
                payment = 2
            product = Cart.objects.filter(user=requests.user, ordered=False)
            product_quantity = Cart.objects.filter(user=requests.user, ordered=False).aggregate(Sum('quantity'))[
                'quantity__sum']
            total_price = \
                Cart.objects.filter(user=requests.user, ordered=False).aggregate(Sum('total_price_with_discount'))[
                    'total_price_with_discount__sum']
            if data.get('promo_code') != '':
                order = Order.objects.create(
                    quantity=product_quantity,
                    total_price=total_price - ((total_price * promo.discount) / 100),
                    user=requests.user,
                    promo=Promocode.objects.filter(name=data.get('promo_code')).first(),
                    delivery_address=data.get('delivery_address'), taking_type=delivery,
                    delivery_point=data.get('delivery_point'), first_name=data.get('first_name'),
                    last_name=data.get('last_name'), phone_number=data.get('phone_number'),
                    payment_type=payment
                )
                order.product.set(product.values_list('product', flat=True))
                order.save()
                for i in product:
                    if i.product.product_quantity == 0:
                        i.ordered = True
                        i.save()
                    elif i.quantity > i.product.product_quantity:
                        i.ordered = True
                        i.save()
                        obj = Cart.objects.create(user=requests.user, product=i.product, name=i.product.name,
                                                  price=i.product.price,
                                                  discount=i.product.discount,
                                                  price_with_discount=i.product.price_with_discount,
                                                  quantity=i.product.product_quantity,
                                                  total_price_with_discount=i.product.product_quantity * i.product.price_with_discount,
                                                  total_price_without_discount=i.product.product_quantity * i.product.price)
                        obj.save()
                        qua = i.product.product_quantity
                        i.product.product_quantity -= qua
                        i.product.save()
                    elif i.quantity < i.product.product_quantity:
                        i.ordered = True
                        i.save()
                        obj = Cart.objects.create(user=requests.user, product=i.product, name=i.product.name,
                                                  price=i.product.price,
                                                  discount=i.product.discount,
                                                  price_with_discount=i.product.price_with_discount,
                                                  quantity=i.quantity,
                                                  total_price_with_discount=i.product.product_quantity * i.product.price_with_discount,
                                                  total_price_without_discount=i.product.product_quantity * i.product.price)
                        obj.save()
                        qua = i.product.product_quantity
                        i.product.product_quantity -= qua
                        i.product.save()
                new_promo = PromoCodeObj.objects.create(user=user, promo=Promocode.objects.filter(
                    name=data.get('promo_code')).first())
                new_promo.save()
            else:
                order = Order.objects.create(
                    quantity=product_quantity,
                    total_price=total_price,
                    user=requests.user,
                    delivery_address=data.get('delivery_address'), taking_type=delivery,
                    delivery_point=data.get('delivery_point'), first_name=data.get('first_name'),
                    last_name=data.get('last_name'), phone_number=data.get('phone_number'),
                    payment_type=payment
                )
                order.product.set(product.values_list('product', flat=True))
                order.save()
                for i in product:
                    if i.product.product_quantity == 0:
                        i.ordered = True
                        i.save()
                    elif i.quantity > i.product.product_quantity:
                        i.ordered = True
                        i.save()
                        obj = Cart.objects.create(user=requests.user, product=i.product, name=i.product.name,
                                                  price=i.product.price,
                                                  discount=i.product.discount,
                                                  price_with_discount=i.product.price_with_discount,
                                                  quantity=i.product.product_quantity,
                                                  total_price_with_discount=i.product.product_quantity * i.product.price_with_discount,
                                                  total_price_without_discount=i.product.product_quantity * i.product.price)
                        obj.save()
                        qua = i.product.product_quantity
                        i.product.product_quantity -= qua
                        i.product.save()
                    elif i.quantity < i.product.product_quantity:
                        i.ordered = True
                        i.save()
                        obj = Cart.objects.create(user=requests.user, product=i.product, name=i.product.name,
                                                  price=i.product.price,
                                                  discount=i.product.discount,
                                                  price_with_discount=i.product.price_with_discount,
                                                  quantity=i.quantity,
                                                  total_price_with_discount=i.product.product_quantity * i.product.price_with_discount,
                                                  total_price_without_discount=i.product.product_quantity * i.product.price)
                        obj.save()
                        qua = i.product.product_quantity
                        i.product.product_quantity -= qua
                        i.product.save()

            return render(requests, 'payment-d.html', {'order_id': order.id})
        elif data.get('payment') == 'byhand':
            if data.get('delivery') == 'pickup':
                delivery = 1
            else:
                delivery = 2
            if data.get('payment') == 'byhand':
                payment = 1
            else:
                payment = 2

            product = Cart.objects.filter(user=requests.user, ordered=False)
            product_quantity = Cart.objects.filter(user=requests.user, ordered=False).aggregate(Sum('quantity'))[
                'quantity__sum']
            total_price = \
                Cart.objects.filter(user=requests.user, ordered=False).aggregate(Sum('total_price_with_discount'))[
                    'total_price_with_discount__sum']
            if data.get('promo_code') != '':
                order = Order.objects.create(
                    quantity=product_quantity,
                    total_price=total_price - ((total_price * promo.discount) / 100),
                    user=requests.user,
                    promo=Promocode.objects.filter(name=data.get('promo_code')).first(),
                    delivery_address=data.get('delivery_address'), taking_type=delivery,
                    delivery_point=data.get('delivery_point'), first_name=data.get('first_name'),
                    last_name=data.get('last_name'), phone_number=data.get('phone_number'),
                    payment_type=payment, payment_status=1
                )
                order.product.set(product.values_list('product', flat=True))
                order.save()
                for i in product:
                    if i.product.product_quantity == 0:
                        i.ordered = True
                        i.save()
                    elif i.quantity > i.product.product_quantity:
                        i.ordered = True
                        i.save()
                        obj = Cart.objects.create(user=requests.user, product=i.product, name=i.product.name,
                                                  price=i.product.price,
                                                  discount=i.product.discount,
                                                  price_with_discount=i.product.price_with_discount,
                                                  quantity=i.product.product_quantity,
                                                  total_price_with_discount=i.product.product_quantity * i.product.price_with_discount,
                                                  total_price_without_discount=i.product.product_quantity * i.product.price)
                        obj.save()
                        qua = i.product.product_quantity
                        i.product.product_quantity -= qua
                        i.product.save()
                    elif i.quantity < i.product.product_quantity:
                        i.ordered = True
                        i.save()
                        obj = Cart.objects.create(user=requests.user, product=i.product, name=i.product.name,
                                                  price=i.product.price,
                                                  discount=i.product.discount,
                                                  price_with_discount=i.product.price_with_discount,
                                                  quantity=i.quantity,
                                                  total_price_with_discount=i.product.product_quantity * i.product.price_with_discount,
                                                  total_price_without_discount=i.product.product_quantity * i.product.price)
                        obj.save()
                        qua = i.product.product_quantity
                        i.product.product_quantity -= qua
                        i.product.save()

                generate_qr_code(order)
                new_promo = PromoCodeObj.objects.create(user=requests.user, promo=Promocode.objects.filter(
                    name=data.get('promo_code')).first())
                new_promo.save()
            else:
                order = Order.objects.create(
                    quantity=product_quantity,
                    total_price=total_price,
                    user=requests.user,
                    delivery_address=data.get('delivery_address'), taking_type=delivery,
                    delivery_point=data.get('delivery_point'), first_name=data.get('first_name'),
                    last_name=data.get('last_name'), phone_number=data.get('phone_number'),
                    payment_type=payment, payment_status=1
                )
                order.product.set(product.values_list('product', flat=True))
                order.save()
                for i in product:
                    if i.product.product_quantity == 0:
                        i.ordered = True
                        i.save()
                    elif i.quantity > i.product.product_quantity:
                        i.ordered = True
                        i.save()
                        obj = Cart.objects.create(user=requests.user, product=i.product, name=i.product.name,
                                                  price=i.product.price,
                                                  discount=i.product.discount,
                                                  price_with_discount=i.product.price_with_discount,
                                                  quantity=i.product.product_quantity,
                                                  total_price_with_discount=i.product.product_quantity * i.product.price_with_discount,
                                                  total_price_without_discount=i.product.product_quantity * i.product.price)
                        obj.save()
                        qua = i.product.product_quantity
                        i.product.product_quantity -= qua
                        i.product.save()
                    elif i.quantity < i.product.product_quantity:
                        i.ordered = True
                        i.save()
                        obj = Cart.objects.create(user=requests.user, product=i.product, name=i.product.name,
                                                  price=i.product.price,
                                                  discount=i.product.discount,
                                                  price_with_discount=i.product.price_with_discount,
                                                  quantity=i.quantity,
                                                  total_price_with_discount=i.product.product_quantity * i.product.price_with_discount,
                                                  total_price_without_discount=i.product.product_quantity * i.product.price)
                        obj.save()
                        qua = i.product.product_quantity
                        i.product.product_quantity -= qua
                        i.product.save()

                generate_qr_code(order)
            return redirect(reverse('profile'))
        else:
            return redirect('/checkout')
    user = requests.user
    card_objs = Cart.objects.filter(user__first_name=user.first_name, user__last_name=user.last_name, ordered=False)
    cart_counter = Cart.objects.filter(user=user, ordered=False).aggregate(Count('user'))
    genre_for_base = Genre.objects.all().order_by('-created_at')[:5]

    total_quantity = 0
    with_discount = 0
    without_discount = 0

    if card_objs:
        total_quantity = Cart.objects.filter(user=user, ordered=False).aggregate(Sum('quantity'))['quantity__sum'] or 0

        with_discount = Cart.objects.filter(user=user, ordered=False).aggregate(
            Sum('total_price_with_discount'))['total_price_with_discount__sum'] or 0

        without_discount = Cart.objects.filter(user=user, ordered=False).aggregate(
            Sum('total_price_without_discount'))['total_price_without_discount__sum'] or 0

    d = {
        'cart_num': cart_counter['user__count'],
        'total_quantity': total_quantity,
        'with_discount': Decimal(with_discount).quantize(Decimal('0.01'), rounding=ROUND_DOWN),
        'without_discount': Decimal(without_discount).quantize(Decimal('0.01'), rounding=ROUND_DOWN),
        'genre_for_base': genre_for_base
    }
    return render(requests, 'checkout.html', context=d)


@login_required(login_url='/login')
def update_cart_view(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    data = json.loads(request.body)
    cart_id = data.get('id')
    delta = -1 if data.get('sign') == '-' else 1
    try:
        cart_item = Cart.objects.get(id=cart_id, user=request.user)
    except Cart.DoesNotExist:
        return JsonResponse({"detail": "product not found"}, status=404)

    product = cart_item.product

    if delta == 1:
        if product.product_quantity < delta:
            return JsonResponse({"detail": "Not enough stock available."}, status=400)

        product.product_quantity -= delta
        product.save()
        cart_item.quantity += delta

    elif delta == -1:
        if cart_item.quantity <= 1:
            cart_item.quantity = 1

        product.product_quantity += 1
        product.save()
        cart_item.quantity -= 1

    cart_item.total_price_with_discount = cart_item.price_with_discount * cart_item.quantity
    cart_item.total_price_without_discount = cart_item.price * cart_item.quantity
    cart_item.save()

    total_quantity = Cart.objects.filter(user=request.user, ordered=False).aggregate(Sum('quantity'))[
                         'quantity__sum'] or 0
    with_discount = Cart.objects.filter(user=request.user, ordered=False).aggregate(
        Sum('total_price_with_discount'))['total_price_with_discount__sum'] or 0

    without_discount = Cart.objects.filter(user=request.user, ordered=False).aggregate(
        Sum('total_price_without_discount'))['total_price_without_discount__sum'] or 0

    saving = without_discount - with_discount

    return JsonResponse(data={"count": cart_item.quantity, "price": {
        "with": cart_item.total_price_with_discount,
        "without": cart_item.total_price_without_discount,
        "total_quantity": total_quantity,
        "saving": Decimal(saving).quantize(Decimal('0.01'), rounding=ROUND_DOWN),
        "with_discount": Decimal(with_discount).quantize(Decimal('0.01'), rounding=ROUND_DOWN),
        "without_discount": Decimal(without_discount).quantize(Decimal('0.01'), rounding=ROUND_DOWN),
    }}, status=200)


@login_required(login_url='/login')
def delete_cart_view(request, pk):
    cart = get_object_or_404(Cart, id=pk)
    try:
        cart.product.product_quantity += cart.quantity
        cart.product.save()
        cart.delete()
    except Exception as e:
        return JsonResponse({"detail": str(e)}, status=400)

    cart_counter = Cart.objects.filter(user=request.user, ordered=False).aggregate(Count('user'))

    total_quantity = Cart.objects.filter(user=request.user, ordered=False).aggregate(Sum('quantity'))[
                         'quantity__sum'] or 0
    with_discount = Cart.objects.filter(user=request.user, ordered=False).aggregate(
        Sum('total_price_with_discount'))['total_price_with_discount__sum'] or 0
    without_discount = Cart.objects.filter(user=request.user, ordered=False).aggregate(
        Sum('total_price_without_discount'))['total_price_without_discount__sum'] or 0
    saving = without_discount - with_discount

    return JsonResponse(data={
        "message": "success",
        "cart_counter": cart_counter['user__count'],
        "total_quantity": total_quantity,
        "with_discount": Decimal(with_discount).quantize(Decimal('0.01'), rounding=ROUND_DOWN),
        "without_discount": Decimal(without_discount).quantize(Decimal('0.01'), rounding=ROUND_DOWN),
        "saving": Decimal(saving).quantize(Decimal('0.01'), rounding=ROUND_DOWN)

    }, status=200)


def delete_order_view(request, pk):
    order = get_object_or_404(Order, id=pk)
    if order.promo is not None:
        used_promo = PromoCodeObj.objects.filter(user_id=request.user.id, promo__name=order.promo.name).first()
        used_promo.delete()

    for i in order.product.all():
        card = Cart.objects.filter(user__id=request.user.id, product__id=i.id, ordered=False).first()
        if card is None:
            ordered_true = Cart.objects.filter(user__id=request.user.id, product__id=i.id, ordered=False)
            quantity = ordered_true.aggregate(Sum('quantity'))['quantity__sum'] or 0
            new_cart = Cart.objects.create(user=request.user, product=i, name=i.name, price=i.price,
                                              discount=i.discount,
                                              price_with_discount=i.price - ((i.discount / 100) * i.price),
                                              quantity=quantity, total_price_with_discount=(i.price * quantity) - (
                        (i.discount / 100) * i.price),
                                              total_price_without_discount=i.price * quantity
                                              )
            new_cart.save()
            ordered_true.delete()
        else:
            ordered_true = Cart.objects.filter(user__id=request.user.id, product__id=i.id, ordered=False)
            quantity = ordered_true.aggregate(Sum('quantity'))['quantity__sum'] or 0
            card.quantity = quantity
            card.total_price_with_discount = quantity * card.price_with_discount
            card.total_price_without_discount = quantity * card.price
            card.save()
            ordered_true.delete()

    try:
        order.delete()
    except Exception as e:
        return JsonResponse({"detail": str(e)}, status=400)
    return JsonResponse(data={
        "message": "success",
    }, status=200)
