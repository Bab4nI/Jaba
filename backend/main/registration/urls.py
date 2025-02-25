from django.urls import path
from .views import send_registration_link, user_list, user_detail, login

urlpatterns = [
    path('send-registration-link/', send_registration_link, name='send-registration-link'),
    path('user/', user_list, name='user-list'),
    path('user/<int:pk>/', user_detail, name='user-detail'),
    path('login/', login, name='login'),
]