from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from  drf_yasg import openapi
from  rest_framework.viewsets import ModelViewSet,GenericViewSet

from drf_yasg.utils import swagger_auto_schema
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ValidationError
from django.utils.decorators import  method_decorator
from django.shortcuts import get_object_or_404

from .serializers import AdminRegistrationSerializer,MerchantRegistrationSerializer,MemberRegistrationSerializer,UserSerializer, \
    LoginSerializer,ChangePasswordSerializer,BulkMembersSerializer,\
        OTPVerificationSerializer,EmailSerializer,ResetPasswordSerializer,ConfirmResetTokenSerializer,\
        UserUpdateSerializer,SuperAdminRegistrationSerializer
from .models import User
import datetime ,requests,json
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import authenticate, login, logout, get_user_model

from django.conf import settings

from rest_framework.parsers import FormParser, MultiPartParser
from .token import default_token_generator
from .utils import get_random_string, generateKey
import base64,pyotp,rsa,coreapi

from django.core.mail import send_mail
from rest_framework import mixins
from .utils import CustomPagination



# class UserViewSet(ModelViewSet):
class UserViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,GenericViewSet):
    
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer
    

class BulkMemberViewSet(ModelViewSet):
    """
    list:
    Retuns a list of all employee
    
    create:
    Create a new employee

    retrieve:
    Return the employee with the given employee

    update:
    Update (full) employee info with the given employee

    partial_update:
    Update (partial) employee info with the given employee

    delete:
    Delete employee with the given employee
    """
    serializer_class = BulkMembersSerializer
    pagination_class = CustomPagination
    def get_queryset(self):
        
        employees = get_user_model().objects.filter(groups__name='member')
        return employees


    def create(self, request, args, *kwargs):
        user_group = request.user.groups.all()[0].name
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if user_group  !='member':  
                result = serializer.save()
                no_of_staffs = len(result['employees'])
                return Response({
                    'code': 201,
                    'status': 'Success',
                    'message': f'{no_of_staffs} staffs created successfully'
                }, status=status.HTTP_201_CREATED)
        
            else: 
                return Response({
                    'code': 400,
                    'status':'error',
                    'message': 'User is not permitted to create this User'
                    }, status=status.HTTP_400_BAD_REQUEST) 
        else:
            default_errors = serializer.errors
            fields = []
            for field in default_errors['employees']:
                row_error = []
                for field_name, field_errors in field.items():
                    error_messages = f'{field_name} is {field_errors[0].code}'
                    if field_errors[0].code == 'unique':
                        error_messages = f'{field_name} already exist'
                    row_error.append(error_messages)
                fields.append({"error":', '.join(row_error)})
            return Response(fields, status=status.HTTP_400_BAD_REQUEST)

class CreateAdminView(APIView):
    # permission_classes= (AllowAny,) #For now, it is open
    # serializer_class = BusinessRegistrationSerializer
    # queryset =User.objects.all()
    # parser_classes = (FileUploadParser,)
    # parser_classes = (FormParser, MultiPartParser)



    # permission_classes = (permissions.IsAuthenticated,)
    # schema = ExtractedDataHistorySchema
    @swagger_auto_schema(request_body=AdminRegistrationSerializer) 
    def post(self, request,*args,**kwargs):
        user_group = request.user.groups.all()[0].name
        """
            Create a MyModel
            ---
            parameters:
                - name: file
                  description: file
                  required: True
                  type: file
            responseMessages:
                - code: 201
                  message: Created
        """
        
        # serializer = self.get_serializer(data=request.data)
        # try:
        
        serializer = AdminRegistrationSerializer(data=request.data, context={'request': request} )
        # import pdb
        # pdb.set_trace()
        
        if  serializer.is_valid():
            if user_group  in ['super-admin','admin']:  
                result=serializer.save()
                email=result['email']
                
                user = User.objects.get(email=email) 
                refresh = RefreshToken.for_user(user)
                
                #Send otp to user 
                try:
                        user = User.objects.get(email=email, is_active=True)
                        keygen = generateKey()
                        key = base64.b32encode(keygen.returnValue(email).encode())
                        OTP = pyotp.TOTP(key, interval=settings.OTP_TIMEOUT)
                        print(OTP.now())
                        subject = 'Profile Verification'
                        message = f'Your verification OTP is {OTP.now()}. Please note, the otp expires in 5 minutes.'
                        from_email = settings.EMAIL_HOST_USER
                        to_list = [email]
                        print(message)
                        send_mail(subject, message, from_email, to_list, fail_silently=False)
                        print("Kindly check your mail to reset your password")  
                        return Response({'code':201,
                                        'status':'success',
                                        'message':'Church Admin User created successfully, Check email for verification code',
                                        'refresh': str(refresh),
                                        'access': str(refresh.access_token),
                                        'access_duration': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
                                        },status=status.HTTP_201_CREATED)
                except User.DoesNotExist:
                        return Response({'message':'User with the email does not exist'}, status=status.HTTP_404_NOT_FOUND)
                
            else: 
                return Response({
                    'code': 400,
                    'status':'error',
                    'message': 'User is not permitted to create this User'
                    }, status=status.HTTP_400_BAD_REQUEST) 
        else:
            default_errors = serializer.errors
            print(default_errors)
            error_message = ''
            for field_name, field_errors in default_errors.items():
                error_message += f'{field_name} is {field_errors[0].code},'
            # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'code': 400,
                'status':'error',
                'message': error_message
                }, status=status.HTTP_400_BAD_REQUEST)
       

class CreateMerchantView(APIView):
    # permission_classes= (AllowAny,) #For now, it is open
    # serializer_class = BusinessRegistrationSerializer
    # queryset =User.objects.all()
    # parser_classes = (FileUploadParser,)
    # parser_classes = (FormParser, MultiPartParser)



    # permission_classes = (permissions.IsAuthenticated,)
    # schema = ExtractedDataHistorySchema
    @swagger_auto_schema(request_body=MerchantRegistrationSerializer) 
    def post(self, request,*args,**kwargs):
        user_group = request.user.groups.all()[0].name

        """
            Create a MyModel
            ---
            parameters:
                - name: file
                  description: file
                  required: True
                  type: file
            responseMessages:
                - code: 201
                  message: Created
        """
        

        serializer = MerchantRegistrationSerializer(data=request.data, context={'request': request} )
        # import pdb
        # pdb.set_trace()
        
        if  serializer.is_valid(): 
            if user_group  in ['super-admin','admin']: 
            
                result=serializer.save(created_by=request.user)
                email=result['email']
                
                user = User.objects.get(email=email) 
                refresh = RefreshToken.for_user(user)
                
                #Send otp to user 
                try:
                        user = User.objects.get(email=email, is_active=True)
                        keygen = generateKey()
                        key = base64.b32encode(keygen.returnValue(email).encode())
                        OTP = pyotp.TOTP(key, interval=settings.OTP_TIMEOUT)
                        print(OTP.now())
                        subject = 'InTime App Profile Verification'
                        message = f'Your verification OTP is {OTP.now()}. Please note, the otp expires in 5 minutes.'
                        from_email = settings.EMAIL_HOST_USER
                        to_list = [email]
                        print(message)
                        send_mail(subject, message, from_email, to_list, fail_silently=False)
                        print("Kindly check your mail to reset your password")  
                        return Response({'code':201,
                                        'status':'success',
                                        'message':'Merchant created successfully, Check email for verification code',
                                        'refresh': str(refresh),
                                        'access': str(refresh.access_token),
                                        'access_duration': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
                                        },status=status.HTTP_201_CREATED)
                except User.DoesNotExist:
                        return Response({'message':'User with the email does not exist'}, status=status.HTTP_404_NOT_FOUND)
            else: 
                    return Response({
                        'code': 400,
                        'status':'error',
                        'message': 'User is not permitted to create this User'
                        }, status=status.HTTP_400_BAD_REQUEST)        

        else:
            default_errors = serializer.errors
            print(default_errors)
            error_message = ''
            for field_name, field_errors in default_errors.items():
                error_message += f'{field_name} is {field_errors[0].code},'
            # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'code': 400,
                'status':'error',
                'message': error_message
                }, status=status.HTTP_400_BAD_REQUEST)

class CreateMemberRegistrationView(APIView):
    # permission_classes= (AllowAny,) #For now, it is open
    # serializer_class = BusinessRegistrationSerializer
    # queryset =User.objects.all()
    # parser_classes = (FileUploadParser,)
    # parser_classes = (FormParser, MultiPartParser)



    # permission_classes = (permissions.IsAuthenticated,)
    # schema = ExtractedDataHistorySchema
    @swagger_auto_schema(request_body=MemberRegistrationSerializer) 
    def post(self, request,*args,**kwargs):
        user_group = request.user.groups.all()[0].name
        """
            Create a MyModel
            ---
            parameters:
                - name: file
                  description: file
                  required: True
                  type: file
            responseMessages:
                - code: 201
                  message: Created
        """
        

        serializer = MemberRegistrationSerializer(data=request.data, context={'request': request} )
        # import pdb
        # pdb.set_trace()
        
        if  serializer.is_valid(): 
            if user_group != 'member': 
                result=serializer.save(created_by=request.user)
                email=result['email']
                
                user = User.objects.get(email=email) 
                refresh = RefreshToken.for_user(user)
                
                #Send otp to user 
                try:
                        user = User.objects.get(email=email, is_active=True)
                        keygen = generateKey()
                        key = base64.b32encode(keygen.returnValue(email).encode())
                        OTP = pyotp.TOTP(key, interval=settings.OTP_TIMEOUT)
                        print(OTP.now())
                        subject = 'HOF Souls Bank App Profile Verification'
                        message = f'Your verification OTP is {OTP.now()}. Please note, the otp expires in 5 minutes.'
                        from_email = settings.EMAIL_HOST_USER
                        to_list = [email]
                        print(message)
                        send_mail(subject, message, from_email, to_list, fail_silently=False)
                        print("Kindly check your mail to reset your password")  
                        return Response({'code':201,
                                        'status':'success',
                                        'message':'Team Lead User created successfully, Check email for verification code',
                                        'refresh': str(refresh),
                                        'access': str(refresh.access_token),
                                        'access_duration': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
                                        },status=status.HTTP_201_CREATED)
                except User.DoesNotExist:
                        return Response({'message':'User with the email does not exist'}, status=status.HTTP_404_NOT_FOUND)
            else: 
                return Response({
                    'code': 400,
                    'status':'error',
                    'message': 'User is not permitted to create this User'
                    }, status=status.HTTP_400_BAD_REQUEST)

        else:
            default_errors = serializer.errors
            print(default_errors)
            error_message = ''
            for field_name, field_errors in default_errors.items():
                error_message += f'{field_name} is {field_errors[0].code},'
            # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'code': 400,
                'status':'error',
                'message': error_message
                }, status=status.HTTP_400_BAD_REQUEST)

class CreateSuperAdminRegistrationView(APIView):
    permission_classes= (AllowAny,) #For now, it is open
    # serializer_class = BusinessRegistrationSerializer
    # queryset =User.objects.all()
    # parser_classes = (FileUploadParser,)
    # parser_classes = (FormParser, MultiPartParser)



    # permission_classes = (permissions.IsAuthenticated,)
    # schema = ExtractedDataHistorySchema
    @swagger_auto_schema(request_body=SuperAdminRegistrationSerializer) 
    def post(self, request,*args,**kwargs):
        """
            Create a MyModel
            ---
            parameters:
                - name: file
                  description: file
                  required: True
                  type: file
            responseMessages:
                - code: 201
                  message: Created
        """
        

        serializer = SuperAdminRegistrationSerializer(data=request.data, context={'request': request} )
        # import pdb
        # pdb.set_trace()
        
        if  serializer.is_valid(): 
            result=serializer.save()
            email=result['email']
            
            user = User.objects.get(email=email) 
            refresh = RefreshToken.for_user(user)
            
            #Send otp to user 
            try:
                    user = User.objects.get(email=email, is_active=True)
                    keygen = generateKey()
                    key = base64.b32encode(keygen.returnValue(email).encode())
                    OTP = pyotp.TOTP(key, interval=settings.OTP_TIMEOUT)
                    print(OTP.now())
                    subject = 'HOF Souls Bank App Profile Verification'
                    message = f'Your verification OTP is {OTP.now()}. Please note, the otp expires in 5 minutes.'
                    from_email = settings.EMAIL_HOST_USER
                    to_list = [email]
                    print(message)
                    send_mail(subject, message, from_email, to_list, fail_silently=False)
                    print("Kindly check your mail to reset your password")  
                    return Response({'code':201,
                                    'status':'success',
                                    'message':'Super User created successfully, Check email for verification code',
                                    'refresh': str(refresh),
                                    'access': str(refresh.access_token),
                                    'access_duration': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
                                    },status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                    return Response({'message':'User with the email does not exist'}, status=status.HTTP_404_NOT_FOUND)
                

        else:
            default_errors = serializer.errors
            print(default_errors)
            error_message = ''
            for field_name, field_errors in default_errors.items():
                error_message += f'{field_name} is {field_errors[0].code},'
            # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'code': 400,
                'status':'error',
                'message': error_message
                }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes=[AllowAny]
    authentication_classes=[]
    
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self,request):
        
        serializer= LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            try:
                user= User.objects.get(email=email)
                refresh = RefreshToken.for_user(user)
            except:
                return Response({'code':401,
                                'status':'error',
                                'message':'User does not exist'},status=status.HTTP_401_UNAUTHORIZED)
                
            
            if user.is_verified:
                if user.is_active:
                    # if user.business and user.business.is_active:
                        if user.check_password(password):
                            the_serializer= UserUpdateSerializer #UserSerializer
                            user_data = the_serializer(user).data
                            
                            # if user.groups.filter(name='member').exists():  
                            #     the_serializer= UserUpdateSerializer #UserSerializer
                                                
                            #     user_data = the_serializer(user).data
                            
                            # elif user.groups.filter(name='').exists():
                            #     the_serializer= UserUpdateSerializer #UserSerializer
                            #     user_data = the_serializer(user).data
                            
                                
                                
                            
                            # else:
                            #     return Response({'code':401,
                            #         'status':'error',
                            #         'message':'User is not authorized. Kindly contact your admin'},status=status.HTTP_401_UNAUTHORIZED)
                        
    
                            
                            return Response({
                                'code':200,
                                'status':'success',
                                'message':'Login Sucessful',
                                'user_info':user_data,
                                # 'business':bus_data,
                                'role': role,
                                'refresh': str(refresh),
                                'access': str(refresh.access_token),
                                'access_duration': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
                                },status=status.HTTP_200_OK)
                                
                        else:
                            return Response({'code':401,
                                'status':'error',
                                'message':'Incorrect Password Inserted'},status=status.HTTP_401_UNAUTHORIZED)
                    
                        
                    # else:
                    #     return Response({'code':401,
                    #         'status':'error',
                    #         'message':'Organization\'s Account is not active. Kindly contact your admin'},status=status.HTTP_401_UNAUTHORIZED)
                else:
                    return Response({'code':401,
                        'status':'error',
                        'message':'User is not active. Kindly contact your admin'},status=status.HTTP_401_UNAUTHORIZED)
                            
            else:
                #Send otp to user 
                try:
                    user = User.objects.get(email=email, is_active=True)
                    keygen = generateKey()
                    key = base64.b32encode(keygen.returnValue(email).encode())
                    OTP = pyotp.TOTP(key, interval=settings.OTP_TIMEOUT)
                    print(OTP.now())
                    subject = 'Profile Verification'
                    message = f'Your verification OTP is {OTP.now()}. Please note, the otp expires in {settings.OTP_TIMEOUT/60} minutes.'
                    from_email = settings.EMAIL_HOST_USER
                    to_list = [email]
                    print(message)
                    print ('token',str(refresh.access_token))
                    send_mail(subject, message, from_email, to_list, fail_silently=False)
                    print("Kindly check your mail to reset your password")                     
                    
                    return Response({'code':406,
                        'status':'error',
                        'message':'User not verified.Kindly check your mail for your verification code',
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'access_duration': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']},status=status.HTTP_406_NOT_ACCEPTABLE)
                except User.DoesNotExist:
                    return Response({'message':'User with the email does not exist'}, status=status.HTTP_404_NOT_FOUND)
   

class UpdatePasswordView(APIView):
    # permission_classes= (AllowAny,) #For now, it is open

    # schema = UpdatePasswordSchema

    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.validated_data["old_password"]
            if not user.check_password(old_password):
                return Response({
                    'status':"failed",
                    'message':"Incorrect Password"
                }, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response({
                'status':"success",
                'message':"Password changed successfully"
            },status=status.HTTP_200_OK)
        default_errors = serializer.errors
        print(default_errors)
        error_message = ''
        for field_name, field_errors in default_errors.items():
            error_message += f'{field_name} is {field_errors[0].code},'
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'code': 400,
            'message': error_message
            }, status=status.HTTP_400_BAD_REQUEST)
        


class OTPVerificationView(APIView):
    # permission_classes=[AllowAny]
    
    @swagger_auto_schema(request_body=OTPVerificationSerializer)
    def post(self, request):
        user = request.user
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            otp_code = serializer.validated_data['otp_code']
            # email= user.email
            email=serializer.validated_data['email']
            
            
            try:
                user = User.objects.get(email=email)
                keygen = generateKey()
                key = base64.b32encode(keygen.returnValue(email).encode())  # Generating Key
                OTP = pyotp.TOTP(key, interval=settings.OTP_TIMEOUT)  # TOTP Model
                print(OTP.verify(otp_code))
                if OTP.verify(otp_code):
                    
                    user.is_verified = True
                    user.save()
                    login(request, user)
                    refresh = RefreshToken.for_user(user)
                    the_serializer= UserUpdateSerializer #UserSerializer      
                    user_data = the_serializer(user).data
                    
                    # if user.groups.filter(name='business').exists():  
                    #     the_serializer= UserUpdateSerializer #UserSerializer
        
                        
                    #     user_data = the_serializer(user).data
                            
                    # elif user.groups.filter(name='member').exists():
                    #     the_serializer= UserUpdateSerializer #UserSerializer

                
                    # else:
                    #     print ('User is not authorized')
                    #     return Response({'code':401,
                    #         'status':'error',
                    #         'message':'User is not authorized. Kindly contact your admin'},status=status.HTTP_401_UNAUTHORIZED)
                        
                    return Response({
                            'code':200,
                            'status':'success',
                            'message':'OTP verification successful',
                            'user_info':user_data,
                            'refresh': str(refresh),
                            'access': str(refresh.access_token),
                            'access_duration': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
                            },status=status.HTTP_200_OK)
                        
                else:
                    return Response({
                        'status': 'failed',
                        'message': 'OTP verification failed'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'message':'User with the email does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            default_errors = serializer.errors
            print(default_errors)
            error_message = ''
            for field_name, field_errors in default_errors.items():
                error_message += f'{field_name} is {field_errors[0].code},'
            # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'code': 400,
                'message': error_message
                }, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordEmailView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []
    # schema = ResetPasswordEmailSchema

    @swagger_auto_schema(request_body=EmailSerializer)
    def post(self,request):
        serializer = EmailSerializer(data=request.data)
        token_generator=default_token_generator
        if serializer.is_valid():
            email_address = serializer.data.get("email").lower()
            print(email_address)
            try:
                user = User.objects.get(email=email_address, is_active=True)
                refresh = RefreshToken.for_user(user)
                keygen = generateKey()
                key = base64.b32encode(keygen.returnValue(email_address).encode())
                OTP = pyotp.TOTP(key, interval=settings.OTP_TIMEOUT)
                otp_data= OTP.now()
                print(otp_data)
                subject = 'Reset Your Password'
                # message = f'Your reset password OTP is {otp_data}. Please note, the otp expires in 5 minutes.'
                message = f'Your reset password link:  or https://staging.swapbase.io/reset/change?otp_code={otp_data}&email={email_address}. Please note, the reset link expires in 5 minutes.'
                from_email = settings.EMAIL_HOST_USER
                to_list = [email_address]
                print(message)
                # send_mail(subject, message, from_email, to_list, fail_silently=False)
                print("Kindly check your mail to reset your password")
                # return Response({'status':'Successful'},status=status.HTTP_200_OK)
                return Response({
                    'status':'Successful', 
                    'otp':f'{otp_data}', 
                    'url': message,
                    'otp_expiry': settings.OTP_TIMEOUT,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'access_duration': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
                    },status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'message':'User with the email does not exist'}, status=status.HTTP_404_NOT_FOUND)
        default_errors = serializer.errors
        print(default_errors)
        error_message = ''
        for field_name, field_errors in default_errors.items():
            error_message += f'{field_name} is {field_errors[0].code},'
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'code': 400,
            'message': error_message
            }, status=status.HTTP_400_BAD_REQUEST)


class ConfirmResetTokenView(APIView):
    permission_classes = (AllowAny,)
    # authentication_classes = []
    # schema = ConfirmResetTokenSchema

    @swagger_auto_schema(request_body=ConfirmResetTokenSerializer)
    def post(self, request):
        serializer = ConfirmResetTokenSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email'].lower()
            token = serializer.validated_data['otp_code']
            try:
                user = User.objects.get(email=email)
                keygen = generateKey()
                key = base64.b32encode(keygen.returnValue(email).encode())  # Generating Key
                OTP = pyotp.TOTP(key, interval=settings.OTP_TIMEOUT)  # TOTP Model
                print(OTP.verify(token))
                if OTP.verify(token):
                    login(request, user)
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'status': 'Successful',
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'message': 'OTP verification successful'
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'status': 'failed',
                        'message': 'OTP verification failed'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'message':'User with the email does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            default_errors = serializer.errors
            print(default_errors)
            error_message = ''
            for field_name, field_errors in default_errors.items():
                error_message += f'{field_name} is {field_errors[0].code},'
            # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'code': 400,
                'message': error_message
                }, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    
    
    permission_classes= (AllowAny,) #For now, it is open

    @swagger_auto_schema(request_body=ResetPasswordSerializer)
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            password_1 = serializer.validated_data["password"]
            password_2 = serializer.validated_data["confirm_password"]
            if password_1 == password_2:
                user = User.objects.get(id=request.user.id)
                user.set_password(password_1)
                user.is_verified = True
                user.save()
                print(user)
                return Response({
                    'code':200,
                    'message':'User password changed successfully',
                    'resolve':'You can now proceed to login'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'code':'400',
                    'message':"Password don't match",
                    'resolve':'Ensure the two passwords are same'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            default_errors = serializer.errors
            print(default_errors)
            error_message = []
            for field_name, field_errors in default_errors.items():
                error_message.append(f'{field_name} is {field_errors[0].code}')
            # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            print(error_message)
            return Response({
                'code': 400,
                'message': ', '.join(error_message),
                'resolve': "Fix error in input"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            
                       
class GetUserView(APIView):
    # permission_classes=[AllowAny]
    # authentication_classes=[]
    
    def get(self,request):
        
        user=request.user
        if user:
            user = User.objects.get(email=user.email)
            refresh = RefreshToken.for_user(user)
            if user.is_verified:
                if user.is_active:
                        
                    
                    if  user.groups.filter(name='church-admin').exists():  
                        the_serializer= UserUpdateSerializer #UserSerializer
                        user_data = the_serializer(user).data
                    
                    elif user.groups.filter(name='member').exists():
                        the_serializer= UserUpdateSerializer #UserSerializer   
                        user_data = the_serializer(user).data
                    
                    elif user.groups.filter(name='team-lead').exists():
                        the_serializer= UserUpdateSerializer #UserSerializer    
                        user_data = the_serializer(user).data
                        
                    
                    elif user.groups.filter(name='super-admin').exists():
                        the_serializer= UserUpdateSerializer #UserSerializer
                        user_data = the_serializer(user).data
                       

                    else:
                        return Response({'code':401,
                            'status':'error',
                            'message':'User is not authorized. Kindly contact your admin'},status=status.HTTP_401_UNAUTHORIZED)
                
                    
                    return Response({
                        'code':200,
                        'status':'success',
                        'message':'Login Sucessful',
                        'user_info':user_data,
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'access_duration': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
                        },status=status.HTTP_200_OK)
                        
                    
                else:
                    return Response({'code':401,
                        'status':'error',
                        'message':'User is not active. Kindly contact your admin'},status=status.HTTP_401_UNAUTHORIZED)
                            
            else:

                return Response({'code':401,
                    'status':'error',
                    'message':'User not verified.Kindly check your mail for your verification code',
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'access_duration': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']},status=status.HTTP_401_UNAUTHORIZED)
                
        else:
            return Response({'code':401,
                            'status':'error',
                            'message':'User does not exist'},status=status.HTTP_401_UNAUTHORIZED)
        