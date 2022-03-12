# Created By  : Sunday Ajayi (http://linkedin.com/in/sunday-ajayi)
# Created Date: 06/03/2022



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from  drf_yasg import openapi
from  rest_framework.viewsets import ModelViewSet,GenericViewSet
from rest_framework.generics import CreateAPIView
from drf_yasg.utils import swagger_auto_schema
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ValidationError
from django.utils.decorators import  method_decorator
from django.shortcuts import get_object_or_404

from .serializers import CommoditySerializer,BulkTransactionSerializer, InventorySerializer,TransactionSerializer,InventoryHistorySerializer
from .models import Inventory,InventoryHistory,Transactions,Commodity
import datetime ,requests,json
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import mixins
from django.db.models import Q


class CreateListMixin:
    """Allows bulk creation of a resource."""
    def get_serializer(self, args, *kwargs):
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True

        return super().get_serializer(*args, **kwargs)
    

class CommodityViewSet(ModelViewSet):
    serializer_class = CommoditySerializer
    # queryset = Category.objects.all()
    # permission_classes= (AllowAny,) #For now, it is open
    # permission_classes = (permissions.IsAuthenticated,IsOwner)
    
    def get_queryset(self):
        user = self.request.user
        user_group = user.groups.all()[0].name
        
        if user_group =='merchant' :
            
            queryset = Commodity.objects.filter(created_by=user)
           
            return queryset
        elif user_group in ['admin','super-admin']:
            queryset = Commodity.objects.filter()
           
            return queryset
            # return queryset
            
    def create(self, request,*args, **kwargs):
        user = self.request.user
        
        serializer=CommoditySerializer(data=request.data)
        
        if serializer.is_valid():

            result=serializer.save(created_by=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 

class InventoryViewSet(ModelViewSet):
    serializer_class = InventorySerializer
    # queryset = Category.objects.all()
    # permission_classes= (AllowAny,) #For now, it is open
    # permission_classes = (permissions.IsAuthenticated,IsOwner)
    
    def get_queryset(self):
        user = self.request.user
        user_group = user.groups.all()[0].name
        
        if user_group =='merchant' :
            
            queryset = Inventory.objects.filter(created_by=user)
           
            return queryset
        else:
            queryset = Inventory.objects.filter()
           
            return queryset
            # return queryset
            
    def create(self, request,*args, **kwargs):
        user = self.request.user
        
        serializer=InventorySerializer(data=request.data)
        
        if serializer.is_valid():

            result=serializer.save(created_by=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
class InventoryHistoryViewSet(ModelViewSet):
    serializer_class = InventorySerializer
    # queryset = Category.objects.all()
    # permission_classes= (AllowAny,) #For now, it is open
    # permission_classes = (permissions.IsAuthenticated,IsOwner)
    
    def get_queryset(self):
        user = self.request.user
        user_group = user.groups.all()[0].name
        
        if user_group =='merchant' :
            
            queryset = InventoryHistory.objects.filter(created_by=user)
           
            return queryset
        else:
            queryset = InventoryHistory.objects.filter()
           
            return queryset
            # return queryset
            
    def create(self, request,*args, **kwargs):
        user = self.request.user
        
        serializer=InventoryHistorySerializer(data=request.data)
        
        if serializer.is_valid():

            result=serializer.save(created_by=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
           
class TransactionsViewSet(ModelViewSet):
    serializer_class = TransactionSerializer
    # queryset = Category.objects.all()
    # permission_classes= (AllowAny,) #For now, it is open
    # permission_classes = (permissions.IsAuthenticated,IsOwner)
    
    def get_queryset(self):
        user = self.request.user
        user_group = user.groups.all()[0].name
        
        if user_group =='merchant' :
            
            queryset = Transactions.objects.filter(vendor=user)
           
            return queryset
        elif user_group =='member':
            queryset = Transactions.objects.filter(created_by=user)
        else:
            queryset = Transactions.objects.filter()
           
            return queryset
            # return queryset
            
    def create(self, request,*args, **kwargs):
        user = self.request.user
        
        serializer=TransactionSerializer(data=request.data)
        
        if serializer.is_valid():

            result=serializer.save(created_by=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
class TheBulkTransactionCreateView(APIView):
    serializer_class = BulkTransactionSerializer
    # permission_classes= (AllowAny,) #For now, it is open
    # parser_classes = (FormParser, MultiPartParser)
    
    
    @swagger_auto_schema(request_body=BulkTransactionSerializer)    
    def post (self,request):
  
        serializer = BulkTransactionSerializer(data=request.data,context={'request': request} )
   
        
        if  serializer.is_valid():
            result = serializer.save(user=request.user)
            
            if result['status'] == 'success':        
                return Response({'code':201,
                                    'status':'success',
                                    'message':str(len(result['data']))+' transactions Processed',
                                    'data':TransactionSerializer(result['data'],many=True).data
                                },status=status.HTTP_201_CREATED)
            else:
                return Response({'code':400,
                                    'status':'failed',
                                    'message':'Transaction unnsuccessful'
                                },status=status.HTTP_400_BAD_REQUEST)
                          
        else:
            return Response({'code':400,
                                'status':'error',
                            'message':'An error occurred',},status=status.HTTP_400_BAD_REQUEST)
                
 