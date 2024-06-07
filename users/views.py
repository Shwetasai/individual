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
import base64


class CustomUserCreateView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')
        role = request.data.get('role', 'customer')

        # Encode user data
        user_data = {
            'email': email,
            'username': username,
            'password': password,
            'role': role
        }
        encoded_user_data = base64.urlsafe_b64encode(json.dumps(user_data).encode()).decode()
        print("Encoded User Data:", encoded_user_data)
        # Send verification email
        verification_link = f"{request.scheme}://{request.get_host()}/users/verify/?data={encoded_user_data}"
        send_mail(
            subject='Verify your email',
            message=f"Click the link to verify your email and complete registration: {verification_link}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({
            "message": "Verification email sent. Please check your email to complete registration.",
            "role": role
        }, status=status.HTTP_201_CREATED)

class VerifyEmailView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        encoded_user_data = request.query_params.get('data')
        if not encoded_user_data:
            return Response({"error": "Invalid verification link."}, status=status.HTTP_400_BAD_REQUEST)

        # Decode user data
        decoded_user_data = json.loads(base64.urlsafe_b64decode(encoded_user_data).decode())
        email = decoded_user_data["email"]
        username = decoded_user_data["username"]
        password = decoded_user_data["password"]
        role = decoded_user_data["role"]

        # Save user data to database
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            user = CustomUser.objects.create_user(email=email, username=username, password=password, role=role)
        user.is_email_verified = True
        user.save()


        return Response({"message": "Registration successful."}, status=status.HTTP_201_CREATED)

class TokenObtainPairView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = TokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class UserLoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors) 
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
