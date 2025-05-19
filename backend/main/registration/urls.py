from django.urls import path
from .views import (
    SendRegistrationLinkView, 
    RegisterView, 
    CustomTokenObtainPairView, 
    PasswordResetRequestView,
    PasswordResetConfirmView,
    ChangeEmailRequestView,
    VerifyEmailCodeView,
    UserListView,
    UpdateAdminGroupsView,
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('send-registration-link/', SendRegistrationLinkView.as_view(), name='send_registration_link'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('register/', RegisterView.as_view(), name='register'),
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('change-email-request/', ChangeEmailRequestView.as_view(), name='change_email_request'),
    path('verify-email-code/', VerifyEmailCodeView.as_view(), name='verify_email_code'),
    path('update-admin-groups/', UpdateAdminGroupsView.as_view(), name='update_admin_groups'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]