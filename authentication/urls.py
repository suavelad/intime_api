from django.urls import path
from .apis import   CreateAdminView,CreateMerchantView,UserViewSet,CreateMemberRegistrationView,\
    LoginView,UpdatePasswordView,OTPVerificationView,ResetPasswordEmailView,ConfirmResetTokenView,\
        ResetPasswordView,GetUserView,CreateSuperAdminRegistrationView
        
from .views import SendMailView
from rest_framework.routers import DefaultRouter
 
router = DefaultRouter()



router.register('users',UserViewSet, 'users')

urlpatterns = router.urls

urlpatterns += [
    path('create/member/', CreateMemberRegistrationView.as_view(), name="create-business"),
    path('create/merchant/', CreateMerchantView.as_view(), name="create-team-lead"),
    path('create/admin/',CreateAdminView.as_view(), name='create-church-admin'),
    path('create/super-admin/',CreateSuperAdminRegistrationView.as_view(), name='create-super-admin'),
    path('login/',LoginView.as_view(), name='login'),
    path('change/password/',UpdatePasswordView.as_view(), name='change-password'),
    path('confirm/otp/',OTPVerificationView.as_view(), name='confirm-otp'),
    path('reset-password/code/',ResetPasswordEmailView.as_view(), name='reset-password-link'),
    path('reset-password/verify-code/',ConfirmResetTokenView.as_view(), name='reset-password-verify-code'),
    path('reset-password/',ResetPasswordView.as_view(), name='reset-password'),
    path('get/user/',GetUserView.as_view(), name='get-user-view'),
    path('sendmail/',SendMailView.as_view(), name='sendmail-view')
    
    
    
    
    
]