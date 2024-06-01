from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CustomUser
from .serializers import CustomUserSerializer, TokenObtainPairSerializer, UserLoginSerializer
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

class CustomUserCreateView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()

        user_email = user.email
        send_mail(
            subject='Welcome to Our Platform',
            message='Thank you for registering!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class TokenObtainPairView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = TokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = RefreshToken.for_user(serializer.validated_data['user'])
        access_token = refresh_token.access_token
        print(access_token)  # Print the access token

        return Response(serializer.validated_data, status=status.HTTP_200_OK)
class UserLoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)  # Debugging: Print errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
