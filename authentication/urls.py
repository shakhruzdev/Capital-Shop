from django.urls import path
from .views import register_view, login_view, logout_view, profile_view, edit_profile_view, exit_card_view, \
    edit_profile_image_view

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('edit_profile/', edit_profile_view, name='edit_profile'),
    path('edit_profile_image/', edit_profile_image_view, name='edit_profile_image'),
    path('exit_card/<int:pk>/', exit_card_view, name='exit_card'),
]
