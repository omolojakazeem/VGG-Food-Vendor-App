from .views import LogoutUser, UserList, UserDetail,ActivateUserView
from django.urls import path, include

from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token
from rest_framework_jwt.views import verify_jwt_token

app_name = 'account'

urlpatterns = [
    path('users_list/', UserList.as_view(), name = 'users_list'),
    path('user_logout/', LogoutUser.as_view(), name='auth_user_logout'),
    path('user_reg/<user_id>/<token>', ActivateUserView.as_view(), name = 'auth_user_reg'),
    path('user_detail/<pk>', UserDetail.as_view(), name = 'user_detail'),

    path('api-token-auth/', obtain_jwt_token),
    path('api-token-refresh/', refresh_jwt_token),
    path('api-token-verify/', verify_jwt_token),
    path('auth/', include('rest_auth.urls')),
]