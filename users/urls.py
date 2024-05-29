from django.urls import path
from .views import CustomUserCreate, TokenObtainPairView, UserLoginView

urlpatterns = [
    path('register/', CustomUserCreate.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
]
