from django.urls import path
from .views import send_registration_link

urlpatterns = [
    path('api/send-registration-link/', send_registration_link, name='send-registration-link'),
]