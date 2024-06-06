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
        serializer = CustomUserSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        custom_user_data = serializer.validated_data
        user = serializer.save()

        user_data_for_encoding = {
            'email': custom_user_data['email'],
            'role': custom_user_data.get('role', 'customer'),
        }
        encoded_user_data = base64.urlsafe_b64encode(json.dumps(user_data_for_encoding).encode()).decode()
        

        verification_link = f"{request.scheme}://{request.get_host()}/users/verify/?data={encoded_user_data}"
        send_mail(
            subject='Verify your email',
            message=f"Click the link to verify your email and complete registration: {verification_link}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[custom_user_data['email']],
            fail_silently=False,
        )
        role = custom_user_data.get('role', 'customer')

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

        decoded_custom_user_data = json.loads(base64.urlsafe_b64decode(encoded_user_data).decode())
        email = decoded_custom_user_data["email"]
        print(email)
        usermodel = CustomUser.objects.get(email=email)
        usermodel.is_email_verified = True
        usermodel.save()

        print(decoded_custom_user_data)
        # serializer = CustomUserSerializer(data=decoded_custom_user_data)
        # serializer.is_valid(raise_exception=True)
        # user = serializer.save()
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
