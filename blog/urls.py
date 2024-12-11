from django.urls import path
from .views import (
    index_view,
    blog_view,
    blog_details_view,
    search_view,
    about_view,
    privacy_policy_view,
    faq_view,
    support_view,
    men_genre_for_base,
    women_genre_for_base,
    baby_genre_for_base
)


# URL patterns
urlpatterns = [
    path('', index_view, name='index'),
    path('blog/', blog_view, name='blog'),
    path('blog/<int:pk>/', blog_details_view, name='blog_details'),
    path('search/', search_view, name='search'),
    path('about/', about_view, name='about'),
    path('privacy_policy/', privacy_policy_view, name='privacy_policy'),
    path('faq/', faq_view, name='faq'),
    path('support/', support_view, name='support'),
    path('men_category/<str:pk>/', men_genre_for_base, name='men_category_by_genre'),
    path('women_category/<str:pk>/', women_genre_for_base, name='women_category_by_genre'),
    path('baby_category/<str:pk>/', baby_genre_for_base, name='baby_category_by_genre'),
]
