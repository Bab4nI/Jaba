from django.urls import path
from .views import send_registration_link, user_list, get_user_profile, RegisterView, CustomTokenObtainPairView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('send-registration-link/', send_registration_link, name='send-registration-link'),
    path('users/', user_list, name='user-list'),
    path('profile/', get_user_profile, name='get_user_profile'),
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]