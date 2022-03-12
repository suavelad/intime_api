from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import (
    AbstractBaseUser,BaseUserManager, PermissionsMixin)

from  .manager import CustomUserManager
from rest_framework_simplejwt.tokens import RefreshToken


 
class User (AbstractBaseUser, PermissionsMixin):
    
    GENDER = (
        ('male','Male'),
        ('female','Female')
    )
    
    USER_TYPE = (
         ('branch-lead','Branch Lead'),
        ('admin','Admin'),
        ('member','Member'),
        ('merchant','Merchant'),
        ('super-admin','Super Admin')
    )

   
    id = models.AutoField(primary_key=True)
    email = models.EmailField( max_length=254, unique=True, db_index=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='member_profile',blank=True,null=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    gender= models.CharField(max_length=10, choices=GENDER, null=True, blank=True)
    dob = models.CharField(max_length=20, null=True, blank=True)
    user_type= models.CharField(max_length=255, choices=USER_TYPE, null=True, blank=True)
    is_verified = models.BooleanField(default=False, null=True, blank=True)
    is_active= models.BooleanField(default=False, null=True, blank=True)
    balance= models.FloatField(null=True, blank=True)
    pending_balance= models.FloatField(null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.IntegerField(null=True, blank=True)

    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    objects = CustomUserManager()


    def __str__(self) -> str:
        return self.email

    
    def tokens (self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh':str(refresh),
            'access': str(refresh.access_token)
        }
