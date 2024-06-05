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
from urllib.parse import urlencode
import json

class CustomUserCreateView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_data = serializer.validated_data
        encoded_user_data = urlencode(user_data)

        verification_link = f"{request.scheme}://{request.get_host()}/users/verify/?{encoded_user_data}"

        send_mail(
            subject='Verify your email',
            message=f"Click the link to verify your email and complete registration: {verification_link}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user_data['email']],
            fail_silently=False,
        )
        role = user_data.get('role', 'customer')

        return Response({
            "message": f"Verification email sent. Please check your email to complete registration.",
            "role": role
        }, status=status.HTTP_201_CREATED)
        return Response({"message": "Verification email sent. Please check your email to complete registration."}, status=status.HTTP_201_CREATED)

class VerifyEmailView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        user_data = request.query_params.dict()
        serializer = CustomUserSerializer(data=user_data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"message": "Registration successful."}, status=status.HTTP_201_CREATED)


class TokenObtainPairView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = TokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = RefreshToken.for_user(serializer.validated_data['user'])
        access_token = refresh_token.access_token
        print(access_token) 

        return Response(serializer.validated_data, status=status.HTTP_200_OK)
class UserLoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors) 
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
