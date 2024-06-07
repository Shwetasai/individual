from django.contrib.auth.models import AbstractBaseUser, Group, Permission, BaseUserManager,PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        print(f"User {user.email} created with is_email_verified={user.is_email_verified}")
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('retailer', 'Retailer'),
        ('customer', 'Customer'),
    )

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    role = models.CharField(max_length=255, default='customer')
    is_retailer = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=False)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return self.email


    class Meta:
        swappable = 'AUTH_USER_MODEL'
    
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_groups',  # Changed to avoid conflicts with the default groups field
        blank=True,
        help_text=('The groups this user belongs to. A user will get all permissions '
                   'granted to each of their groups.'),
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions',  # Changed to avoid conflicts with the default user_permissions field
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='customuser',
    )
