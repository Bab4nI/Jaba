from django.urls import path
from .views import (
    SendRegistrationLinkView, 
    RegisterView, 
    CustomTokenObtainPairView, 
    PasswordResetRequestView,
    PasswordResetConfirmView,
    ChangeEmailRequestView,
    VerifyEmailCodeView,
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('password/reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('send-registration-link/', SendRegistrationLinkView.as_view(), name='send-registration-link'),
    path('change-email/', ChangeEmailRequestView.as_view(), name='change_email'),
    path('verify-email-code/', VerifyEmailCodeView.as_view(), name='verify_email_code'),
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]