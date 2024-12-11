from django.urls import path

from .views import (
    categories_view,
    product_detail_view,
    cart_view,
    add_to_cart,
    like_view,
    checkout_view,
    update_cart_view,
    delete_cart_view,
    delete_order_view
)

urlpatterns = [
    path('categories/', categories_view, name='categories'),
    path('products/<int:pk>/', product_detail_view, name='product_detail'),
    path('cart/', cart_view, name='cart'),
    path('add_to_cart/<int:pk>/', add_to_cart, name='add_to_cart'),
    path('like/<int:pk>/', like_view, name='like'),
    path('checkout/', checkout_view, name='checkout'),
    path('update_cart/', update_cart_view, name='update_cart'),
    path('delete_cart/<int:pk>/', delete_cart_view, name='delete_cart'),
    path('delete_order/<int:pk>/', delete_order_view, name='delete_order'),
]
