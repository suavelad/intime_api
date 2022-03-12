from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

# Create your views here.
from django.core.mail import send_mail




class SendMailView(APIView):
    permission_classes= (AllowAny,) #For now, it is open
    
    def get(self, request,*args,**kwargs):
        print('started api')
        
        to_list = ['sunnexajayi@gmail.com']
        # from_email='info@swapbase.io'
        from_email = 'sunnexajayi@gmail.com'
        message = 'LOVE GOD'
        subject = 'TESTING'
        a=send_mail(subject, message, from_email, to_list, fail_silently=False)

        print(a)
        
        return Response({'data':'mail sent'})
