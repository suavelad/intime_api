
import datetime
from django.conf import settings
from rest_framework import serializers
from .models import User
from rest_framework.generics import get_object_or_404
from django.core.mail import  send_mail
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from decouple  import config
from rest_framework.exceptions import ValidationError
from .utils import Base64ImageField, get_random_string, custom_normalize_email


domain = config('domain')

             
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model=Group
        fields = ('name',)     
        
class UserSerializer(serializers.ModelSerializer): 
    
    class Meta:
        model = User
        # fields = ('__all__')
        exclude = ('is_active','is_verified','password','is_superuser','user_permissions','groups' )
        
      
class UserUpdateSerializer(serializers.ModelSerializer): 
    
    class Meta:
        model = User
        # fields = ('__all__')
        exclude = ('is_active','is_verified','password','is_superuser','user_permissions','groups' )
        

      
class MemberRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    gender = serializers.CharField(required=True)
    dob = serializers.CharField(required=False)
    password = serializers.CharField(required=True)
    phone= serializers.CharField(required=True)
    image = serializers.ImageField(required=False)

    
    
    class Meta:
        model = User
        fields = ('__all__')
        
        
    
    def create(self,validated_data):
        request = self.context.get('request')
        user = request.user
        password = validated_data.pop('password') 
        email = validated_data['email']
        
        try:
            existing_user = User.objects.get(email=email)   
        except:
            existing_user = ''
            
        if not existing_user:
   
            mem = User.objects.create(user_type='member',created_by=user.id,**validated_data)
                
            mem.set_password(password)
            
            group= Group.objects.get(name='member')
            mem.is_verified=False
            mem.save()
            mem.groups.add(group)
            
             # SEND MAIL TO USER
            subject = 'Account Activation on InTime Shopping App'
            message = f'Dear {mem.first_name} {mem.last_name}, \InTime has onboarded you as a member on InTIme Shopping Application. Your temporary login details is\
            \nemail={mem.email}\npassword={password}\nKindly visit {domain} to reset your password or download our mobile app using \
            the link below \
            {domain}.'
            from_email = settings.EMAIL_HOST_USER
            to_list = [mem.email]
            print(message)
            send_mail(subject, message, from_email, to_list, fail_silently=True)
            
                
        else:
            raise serializers.ValidationError({'code': 400,
                                                'status':'error',
                                                'message': 'User already exist'})
       
            
        return validated_data


class MiniMemberSerializer(serializers.ModelSerializer):
    """
    Mini Serializer for Members
    """
    class Meta:
        model = User
        read_only_fields = ('id', 'time_created', 'last_login', 'date_created', 'created_by')
        exclude = ('groups', 'is_superuser',   'user_permissions',  'is_active', 'password', 'image')
        # extra_kwargs = {'phone_number': {'required': True}}


    def validate_phone_number(self, data):
        if User.objects.filter(phone_number=data).exists():
            raise ValidationError(detail="User with phone number already exist", code="unique")
        return data

    def validate_email(self, data):
        if User.objects.filter(email=data).exists():
            raise ValidationError(detail="User with email already exist", code="unique")
        return data
    
    
class BulkMembersSerializer(serializers.Serializer):
    members = MiniMemberSerializer(required=True, many=True)

    def create(self, validated_data):
        members = validated_data['members']
        
        # created_by = validated_data['created_by']
        request = self.context.get('request')
        created_by = request.user.id
        for member in members:
           
            member['email'] = custom_normalize_email(member['email'])
            password = get_random_string(8)
            
            mem = User.objects.create(user_type='member',created_by=created_by, **member)
            mem.is_active = True
            mem.set_password(password)
            group = Group.objects.get(name='member')
            mem.save()
            mem.groups.add(group)
            
            # SEND MAIL TO USER
            subject = 'Member Account Activation on Intime App'
            message = f'Dear {mem.first_name} {mem.last_name}, \InTime has onboarded you as a member on InTime Application. Your temporary login details is\
            \nemail={mem.email}\npassword={password}\nKindly visit {domain} to reset your password or download our mobile app using \
            the link below \
            {domain}.'
            from_email = settings.EMAIL_HOST_USER
            to_list = [mem.email]
            print(message)
            send_mail(subject, message, from_email, to_list, fail_silently=True)
        return validated_data


class MerchantRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    gender = serializers.CharField(required=True)
    dob = serializers.CharField(required=False)
    password = serializers.CharField(required=True)
    phone= serializers.CharField(required=True)
    image = serializers.ImageField(required=False)

    
    
    class Meta:
        model = User
        fields = ('__all__')
        
        
    
    def create(self,validated_data):
        request = self.context.get('request')
        user = request.user
        password = validated_data.pop('password') 
        email = validated_data['email']
        
        try:
            existing_user = User.objects.get(email=email)   
        except:
            existing_user = ''
            
        if not existing_user:
   
            mem = User.objects.create(user_type='merchant',created_by=user.id,**validated_data)
                
            mem.set_password(password)
            
            group= Group.objects.get(name='merchant')
            mem.is_verified=False
            mem.save()
            mem.groups.add(group)
            
             # SEND MAIL TO USER
            subject = '{mem.branch.name} {mem.unit.name} Merchant Account Activation on InTIme Shopping App'
            message = f'Dear {mem.first_name} {mem.last_name}, \nInTIme Shopping has onboarded you as  merchant on InTIme Shopping Application. Your temporary login details is\
            \nemail={mem.email}\npassword={password}\nKindly visit {domain} to reset your password or download our mobile app using \
            the link below \
            {domain}.'
            from_email = settings.EMAIL_HOST_USER
            to_list = [mem.email]
            print(message)
            send_mail(subject, message, from_email, to_list, fail_silently=True)
            
                
        else:
            raise serializers.ValidationError({'code': 400,
                                                'status':'error',
                                                'message': 'User already exist'})
       
            
        return validated_data

class AdminRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    gender = serializers.CharField(required=True)
    dob = serializers.CharField(required=False)
    password = serializers.CharField(required=True)
    phone= serializers.CharField(required=True)
    image = serializers.ImageField(required=False)
    branch = serializers.IntegerField(required=False)

    
    
    class Meta:
        model = User
        fields = ('__all__')
        
        
    
    def create(self,validated_data):
        request = self.context.get('request')
        user = request.user
        password = validated_data.pop('password') 
        email = validated_data['email']
        
        try:
            existing_user = User.objects.get(email=email)   
        except:
            existing_user = ''
            
        if not existing_user:
   
            mem = User.objects.create(user_type='admin',created_by=user.id,**validated_data)
                
            mem.set_password(password)
            
            group= Group.objects.get(name='admin')
            mem.is_verified=False
            mem.save()
            mem.groups.add(group)
            
             # SEND MAIL TO USER
            subject = '{mem.branch.name} Admin  Account Activation for HOF Souls bank App'
            message = f'Dear {mem.first_name} {mem.last_name}, \nInTIme  has onboarded you as admin on InTIme Shopping Application. Your temporary login details is\
            \nemail={mem.email}\npassword={password}\nKindly visit {domain} to reset your password or download our mobile app using \
            the link below \
            {domain}.'
            from_email = settings.EMAIL_HOST_USER
            to_list = [mem.email]
            print(message)
            send_mail(subject, message, from_email, to_list, fail_silently=True)
            
                
        else:
            raise serializers.ValidationError({'code': 400,
                                                'status':'error',
                                                'message': 'User already exist'})
       
            
        return validated_data


class SuperAdminRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    dob = serializers.CharField(required=False)
    gender = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    phone= serializers.CharField(required=True)
    image = serializers.ImageField(required=False)

    
    
    class Meta:
        model = User
        fields = ('__all__')
        
        
    
    def create(self,validated_data):
        request = self.context.get('request')
        user = request.user
        password = validated_data.pop('password') 
        email = validated_data['email']
        
        try:
            existing_user = User.objects.get(email=email)   
        except:
            existing_user = ''
            
        if not existing_user:
   
            mem = User.objects.create(user_type='super-admin',created_by=user.id,**validated_data)
                
            mem.set_password(password)
            
            group= Group.objects.get(name='super-admin')
            mem.is_verified=False
            mem.is_active=True
            mem.save()
            mem.groups.add(group)
            
             # SEND MAIL TO USER
            # subject = 'Super Admin Account Activation on HOF Souls bank App'
            # message = f'Dear {mem.first_name} {mem.last_name}, \nHOF has onboarded you as a Super Admin on HOF Souls bank Application. Your temporary login details is\
            # \nemail={mem.email}\npassword={password}\nKindly visit {domain} to reset your password or download our mobile app using \
            # the link below \
            # {domain}.'
            # from_email = settings.EMAIL_HOST_USER
            # to_list = [mem.email]
            # print(message)
            # send_mail(subject, message, from_email, to_list, fail_silently=True)
            
                
        else:
            raise serializers.ValidationError({'code': 400,
                                                'status':'error',
                                                'message': 'User already exist'})
       
            
        return validated_data

     
class LoginSerializer(serializers.Serializer):
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    
    
    def validate_new_password(self,value):
        validate_password(value)
        return value
    

class OTPVerificationSerializer(serializers.Serializer):
    otp_code = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    

class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    
class ResetPasswordSerializer(serializers.Serializer):
    
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
    
  
class ConfirmResetTokenSerializer (serializers.Serializer):
    otp_code = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

