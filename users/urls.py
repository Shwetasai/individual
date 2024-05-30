from django.urls import path
from .views import CustomUserCreateView, TokenObtainPairView, UserLoginView

urlpatterns = [
    path('create/', CustomUserCreateView.as_view(), name='create_user'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/', UserLoginView.as_view(), name='user_login'),
]
