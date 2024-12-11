from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from blog.models import Post, Category, Tag, Comment, Reply
from django.shortcuts import get_object_or_404
from store.models import Product, Genre, Color, Size, Brand
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from store.models import CATEGORY_CHOICES, Cart, Like
from django.db.models import Count

User = get_user_model()
CATEGORY = {name: value for value, name in CATEGORY_CHOICES}


@login_required(login_url='/login')
def men_genre_for_base(request, pk):
    genre_base = Product.objects.filter(genre__name=pk, category=1)
    cart_counter = Cart.objects.filter(user=request.user, ordered=False).aggregate(Count('user'))
    cart_items = Cart.objects.filter(user=request.user, ordered=False).values_list('product_id', flat=True)
    liked_products = Like.objects.filter(user=request.user).values_list('product_id', flat=True)
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
            genre_base = genre_base.filter(size__name=size)

        if color:
            genre_base = genre_base.filter(color__name=color)

        if genre:
            genre_base = genre_base.filter(genre__name__in=genre)

        if brand:
            genre_base = genre_base.filter(brand__name__in=brand)

        if from_amount or to_amount:
            genre_base = genre_base.filter(price_with_discount__gte=from_amount, price_with_discount__lte=to_amount)

    d = {
        'products': genre_base,
        'cart_items': cart_items,
        'liked_products': liked_products,
        'sizes': sizes,
        'colors': colors,
        'genres': genres,
        'brands': brands,
        'cart_num': cart_counter['user__count'],
    }
    return render(request, 'categories.html', d)


@login_required(login_url='/login')
def women_genre_for_base(request, pk):
    genre_base = Product.objects.filter(genre__name=pk, category=2)
    cart_counter = Cart.objects.filter(user=request.user, ordered=False).aggregate(Count('user'))
    cart_items = Cart.objects.filter(user=request.user, ordered=False).values_list('product_id', flat=True)
    liked_products = Like.objects.filter(user=request.user).values_list('product_id', flat=True)
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
            genre_base = genre_base.filter(size__name=size)

        if color:
            genre_base = genre_base.filter(color__name=color)

        if genre:
            genre_base = genre_base.filter(genre__name__in=genre)

        if brand:
            genre_base = genre_base.filter(brand__name__in=brand)

        if from_amount or to_amount:
            genre_base = genre_base.filter(price_with_discount__gte=from_amount, price_with_discount__lte=to_amount)

    d = {
        'products': genre_base,
        'cart_items': cart_items,
        'liked_products': liked_products,
        'sizes': sizes,
        'colors': colors,
        'genres': genres,
        'brands': brands,
        'cart_num': cart_counter['user__count'],
    }
    return render(request, 'categories.html', d)


@login_required(login_url='/login')
def baby_genre_for_base(request, pk):
    genre_base = Product.objects.filter(genre__name=pk, category=3)
    cart_counter = Cart.objects.filter(user=request.user, ordered=False).aggregate(Count('user'))
    cart_items = Cart.objects.filter(user=request.user, ordered=False).values_list('product_id', flat=True)
    liked_products = Like.objects.filter(user=request.user).values_list('product_id', flat=True)
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
            genre_base = genre_base.filter(size__name=size)

        if color:
            genre_base = genre_base.filter(color__name=color)

        if genre:
            genre_base = genre_base.filter(genre__name__in=genre)

        if brand:
            genre_base = genre_base.filter(brand__name__in=brand)

        if from_amount or to_amount:
            genre_base = genre_base.filter(price_with_discount__gte=from_amount, price_with_discount__lte=to_amount)

    d = {
        'products': genre_base,
        'cart_items': cart_items,
        'liked_products': liked_products,
        'sizes': sizes,
        'colors': colors,
        'genres': genres,
        'brands': brands,
        'cart_num': cart_counter['user__count'],
    }
    return render(request, 'categories.html', d)


@login_required(login_url='/login')
def index_view(request):
    posts = Post.objects.all().order_by('-created_at')[:3]
    category_value = CATEGORY.get(request.GET.get('category', '').upper())
    product = Product.objects.filter(category=category_value)
    user_gender = request.user.gender
    trending = Product.objects.all().order_by('-rating')[:5]
    genre_for_base = Genre.objects.all().order_by('-created_at')[:5]

    cart_counter = Cart.objects.filter(user=request.user, ordered=False).aggregate(Count('user'))
    cart_items = Cart.objects.filter(user=request.user, ordered=False).values_list('product_id', flat=True)
    liked_products = Like.objects.filter(user=request.user).values_list('product_id', flat=True)

    search_query = request.GET.get('search', '')
    if search_query:
        return redirect('search')

    if user_gender == 2:
        products = Product.objects.filter(category=1)
    elif user_gender == 3:
        products = Product.objects.filter(category=2)
    else:
        products = []

    context = {
        'posts': posts,
        'trending': trending,
        'products': products,
        'user_gender': user_gender,
        'product': product,
        'cart_items': cart_items,
        'liked_products': liked_products,
        'cart_num': cart_counter['user__count'],
        'genre_for_base': genre_for_base,
    }
    return render(request, 'index.html', context)


@login_required(login_url='/login')
def blog_view(request):
    cat = request.GET.get('cat')
    tag = request.GET.get('tag')
    if tag:
        posts = Post.objects.filter(tags=tag)
    elif cat:
        posts = Post.objects.filter(categories_id=cat)
    else:
        posts = Post.objects.all().order_by('-created_at')

    paginator = Paginator(posts, 2)
    tags = Tag.objects.all()
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    cart_counter = Cart.objects.filter(user=request.user, ordered=False).aggregate(Count('user'))
    recent_posts = Post.objects.all().order_by('-created_at')[:4]
    genre_for_base = Genre.objects.all().order_by('-created_at')[:5]
    category_post_counts = [
        (category, Post.objects.filter(categories=category).count()) for category in Category.objects.all()
    ]

    context = {
        'posts': page,
        'tags': tags,
        'page': page,
        'category_post_counts': category_post_counts,
        'recent_posts': recent_posts,
        'cart_num': cart_counter['user__count'],
        'genre_for_base': genre_for_base,
    }
    return render(request, 'blog.html', context)


@login_required(login_url='/login')
def blog_details_view(request, pk):
    # cat = request.GET.get('category')
    # tag = request.GET.get('tag')
    # if tag:
    #     post = Post.objects.filter(tags=tag)
    # elif cat:
    #     post = Post.objects.filter(category_id=cat)
    # else:
    #     post = Post.objects.all().order_by('-created_at')

    post = get_object_or_404(Post, pk=pk)
    comments = Comment.objects.filter(post=post)
    categories = Category.objects.all()
    tags = Tag.objects.all()
    recent_posts = Post.objects.all().order_by('-created_at')[:4]
    category_post_counts = [
        (category, Post.objects.filter(categories=category).count()) for category in Category.objects.all()
    ]
    cart_counter = Cart.objects.filter(user=request.user, ordered=False).aggregate(Count('user'))
    previous_post = Post.objects.filter(created_at__lt=post.created_at).order_by('-created_at').first()
    next_post = Post.objects.filter(created_at__gt=post.created_at).order_by('-created_at').first()
    genre_for_base = Genre.objects.all().order_by('-created_at')[:5]

    comments_with_reply_count = Comment.objects.filter(post_id=pk).annotate(num_replies=Count(
        'replies')).order_by('-num_replies').first()

    if request.method == 'POST':
        if 'comment' in request.POST:
            comment_message = request.POST.get('comment')
            Comment.objects.create(
                user=request.user,
                post=post,
                message=comment_message,
            )
            return redirect('blog_details', pk=post.pk)

        elif 'reply' in request.POST:
            reply_message = request.POST.get('message')
            comment_id = request.POST.get('comment_id')
            comment = get_object_or_404(Comment, id=comment_id)
            Reply.objects.create(
                user=request.user,
                comment=comment,
                message=reply_message
            )
            return redirect('blog_details', pk=post.pk)

    context = {
        'post': post,
        'comments': comments,
        'categories': categories,
        'tags': tags,
        'category_post_counts': category_post_counts,
        'previous_post': previous_post,
        'next_post': next_post,
        'recent_posts': recent_posts,
        'cart_num': cart_counter['user__count'],
        'comments_with_reply_count': comments_with_reply_count,
        'genre_for_base': genre_for_base,
    }
    return render(request, 'blog-details.html', context)


@login_required(login_url='/login')
def search_view(request):
    search_query = request.GET.get('search', '')
    products = Product.objects.filter(name__icontains=search_query) if search_query else Product.objects.none()
    cart_counter = Cart.objects.filter(user=request.user, ordered=False).aggregate(Count('user'))
    genre_for_base = Genre.objects.all().order_by('-created_at')[:5]
    context = {
        'search_query': search_query,
        'products': products,
        'cart_num': cart_counter['user__count'],
        'genre_for_base': genre_for_base,
    }
    return render(request, 'search.html', context)


@login_required(login_url='/login')
def about_view(request):
    return render(request, 'about.html')


@login_required(login_url='/login')
def privacy_policy_view(request):
    return render(request, 'privacy.html')


@login_required(login_url='/login')
def faq_view(request):
    return render(request, 'faq.html')


@login_required(login_url='/login')
def support_view(request):
    return render(request, 'support.html')
