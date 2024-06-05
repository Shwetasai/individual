from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('retailer', 'Retailer'),
        ('customer', 'Customer'),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    is_retailer = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
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
