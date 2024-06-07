from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
import base64
import json
from django.utils.translation import gettext as _

class CustomUserSerializer(serializers.ModelSerializer):
    is_retailer = serializers.SerializerMethodField()
    is_customer = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'role', 'is_retailer' , 'is_customer']
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
        role = validated_data.get('role', 'customer')
        validated_data['is_retailer'] = (role == 'retailer')
        validated_data['is_customer'] = (role == 'customer')
        validated_data['is_email_verified'] = False
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()

        user_data = {
            'email': user.email,
            'username': user.username,
            'password': password,
            'role': user.role,
        }
        encoded_user_data = base64.urlsafe_b64encode(json.dumps(user_data).encode()).decode()
        request = self.context.get('request')
        verification_link = f"{request.scheme}://{request.get_host()}/users/verify/?data={encoded_user_data}"
        send_mail(
            'Welcome to Our Platform',
            f'Thank you for registering! Please verify your email: {verification_link}',
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

        user = authenticate(request=self.context.get('request'), email=email, password=password)
        if user is None:
            raise serializers.ValidationError(_('Invalid credentials'), code='authorization')


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

        user = authenticate(request=self.context.get('request'), email=email, password=password)
        if user is None:
            raise serializers.ValidationError(_('Invalid credentials'), code='authorization')

        if not user.is_email_verified:
            raise serializers.ValidationError(_('Email is not verified'), code='authorization')

        refresh = RefreshToken.for_user(user)
        return {
            'access_token': str(refresh.access_token),
            'id': user.id,
            'email': user.email,
            "role":user.role
        }