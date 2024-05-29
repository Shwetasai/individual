from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    is_retailer = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)

    class Meta:
        swappable = 'AUTH_USER_MODEL'

# Define the intermediate models for groups and permissions
class UserGroup(models.Model):
    customuser = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

class UserPermission(models.Model):
    customuser = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
