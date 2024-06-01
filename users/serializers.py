from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings

class CustomUserSerializer(serializers.ModelSerializer):
    is_retailer = serializers.SerializerMethodField()
    is_customer = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'is_retailer', 'is_customer']
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_retailer(self, obj):
        if isinstance(obj, dict):
            return obj.get('role') == 'retailer'
        return obj.role == 'retailer'

    def get_is_customer(self, obj):
        if isinstance(obj, dict):
            return obj.get('role') == 'customer'
        return obj.role == 'customer'

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        send_mail(
            'Welcome to Our Platform',
            'Thank you for registering!',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return user


class TokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError('Invalid credentials')

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'id': user.id,
            'email': user.email,
        }

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError('Invalid credentials')

        refresh = RefreshToken.for_user(user)
        return {
            'access_token': str(refresh.access_token),
            'id': user.id,
            'email': user.email,
        }