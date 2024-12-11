from django.urls import path
from .views import pay_online_view, add_card, add_card_details_view

urlpatterns = [
    path('payment-d/<int:pk>/', pay_online_view, name='pay_online'),
    path('add-card/', add_card, name='add_card'),
    path('add_card_details/', add_card_details_view, name='add_card_details'),
]
