from django.urls import path
from .views import GetUserProfileView

urlpatterns = [
    path('profile/', GetUserProfileView.as_view(), name='get_user_profile'),  # /api/profile
]