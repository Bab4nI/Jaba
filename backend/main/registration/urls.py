from django.urls import path
from .views import SendRegistrationLinkView, RegisterView, CustomTokenObtainPairView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('send-registration-link/', SendRegistrationLinkView.as_view(), name='send-registration-link'),  # /api/send-registration-link
    path('register/', RegisterView.as_view(), name='register'),  # /api/register
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # /api/token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # /api/token/refresh
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),  # /api/token/verify
]