# user_profile/urls.py
from django.urls import path
from .views import GetUserProfileView, GroupUsersView, AdminsView, GroupsListView

urlpatterns = [
    path('profile/', GetUserProfileView.as_view(), name='get_user_profile'),  # /api/profile
    path('group-users/', GroupUsersView.as_view(), name='group_users'),  # /api/group-users/?group=КТсо2-4
    path('admins/', AdminsView.as_view(), name='admins'),  # /api/admins/
    path('groups/', GroupsListView.as_view(), name='groups_list'),  # /api/groups/
]