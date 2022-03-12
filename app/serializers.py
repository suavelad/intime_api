import datetime
from django.conf import settings
from rest_framework import serializers
from .models import Inventory,InventoryHistory,Transactions,Commodity,Category
from authentication.models import User
from rest_framework.generics import get_object_or_404
from django.core.mail import  send_mail
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from decouple  import config
from rest_framework.exceptions import ValidationError
from .utils import Base64ImageField, get_random_string, custom_normalize_email


 
class CommoditySerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField(read_only=True)
    vendor = serializers.SerializerMethodField(read_only=True)
    
    
    def get_vendor(self,obj):
        if obj.created_by:
            u= User.objects.get(id=obj.created_by.id)
            return f'{u.firstname} {u.last_name}'
        else:
            None
    def get_category_name(self, obj):
        if obj.category:
            c = Category.objects.get(id=obj.category.id)
            return c.name
        else:
            return None
        
    class Meta:
        model=Commodity
        fields = ['category_name','vendor','name','description','category','type','unit_price','is_active']
        read_only = ['created_by','created_date','created_time']


class InventorySerializer(serializers.ModelSerializer):
    commodity_name = serializers.SerializerMethodField(read_only=True)
    vendor = serializers.SerializerMethodField(read_only=True)
    
    
    def get_vendor(self,obj):
        if obj.created_by:
            u= User.objects.get(id=obj.created_by.id)
            return f'{u.firstname} {u.last_name}'
        else:
            None
    def get_commodity_name(self, obj):
        if obj.commodity:
            c = Commodity.objects.get(id=obj.commodity.id)
            return c.name
        else:
            return None
        
    class Meta:
        model=Inventory
        fields = ['commodity_name','vendor','initial_quantity','quantity_used','quantity_left']
        read_only = ['created_by','created_date','created_time']

class InventoryHistorySerializer(serializers.ModelSerializer):
    commodity_name = serializers.SerializerMethodField(read_only=True)
    vendor = serializers.SerializerMethodField(read_only=True)
    
    
    def get_vendor(self,obj):
        if obj.created_by:
            u= User.objects.get(id=obj.created_by.id)
            return f'{u.firstname} {u.last_name}'
        else:
            None
    def get_commodity_name(self, obj):
        if obj.commodity:
            c = Commodity.objects.get(id=obj.commodity.id)
            return c.name
        else:
            return None
     
    class Meta:
        model=InventoryHistory
        fields = ['commodity_name','vendor','initial_quantity','quantity_used','quantity_left']
        read_only = ['created_by','created_date','created_time']


class TransactionSerializer(serializers.ModelSerializer): 
    merchant = serializers.SerializerMethodField(read_only=True)
    user = serializers.SerializerMethodField(read_only=True)
    commodity_name = serializers.SerializerMethodField(read_only=True)
    
    def get_merchant(self,obj):
        if obj.vendor:
            u = User.objects.get(id=obj.vendor.id)
            return f'{u.last_name} {u.first_name}'
    
    def get_user(self,obj):
        if obj.user:
            u = User.objects.get(id=obj.user.id)
            return f'{u.last_name} {u.first_name}'


    def get_commodity_name(self, obj):
        if obj.commodity:
            c = Commodity.objects.get(id=obj.commodity.id)
            return c.name
        else:
            return None
        
    class Meta:
        model = Transactions
        fields = ['id','commodity_name','commodity','quantity','unit_price','vendor','merchant','user']
        read_only = ['payment_status','amount','created_date','created_time']

class BulkTransactionSerializer(serializers.ModelSerializer): 
    orders = TransactionSerializer(many=True,required=True)
    
    
    
    def create(self, validated_data):
        orders = validated_data['orders']
        
        # created_by = validated_data['created_by']
        request = self.context.get('request')
        
        # Verify payment with payment gateway
        ref = orders[0]['ref']
        gateway_url = 'https:gateway.com/verify/'+ref   #sample url
        access_token = 'xxxxx'
        headers= {'Authorization': f'Bearer {access_token}', 'content_type': 'application/json'}
        r = request.post(gateway_url,headers=headers)
        resp = r.json()
        
       
        # Get total amount:
        total_amount = 0
        for order in orders:
            total_amount += order.quantity * order.unit_price
        
        
        for order in orders:
            amount = order.quantity * order.unit_price
            
            if resp['data']['status'].lower() == 'success' and resp['data']['amount'] == total_amount:
                p_status = 'success'
            
            else: 
                p_status = 'failed'
                

            mem = Transactions.objects.create(user=request.user,payment_status=p_status,amount=amount, **order)
            mem.save()
            
            if  p_status == 'success':
                # Credit merchant
                m = User.objects.get(id=mem.vendor.id)
                m.balance = amount
                m.save()
                
                # update inventory
                inv = Inventory.objects.get(commodity =mem.commodity)
                inv.quantity_used = inv.quantity_used + mem.quantity
                inv.quantity_left = inv.quantity_left - mem.quantity
                inv.save()
            

                try:
                    # SEND MAIL TO USER
                    subject = 'Transaction Confirmation'
                    message = f'Dear {mem.first_name} {mem.last_name}, \n This is to confirm that your transaction of about # {total_amount}\
                    \n was successful.'  
                    from_email = settings.EMAIL_HOST_USER
                    to_list = [mem.email]
                    print(message)
                    send_mail(subject, message, from_email, to_list, fail_silently=True)
                except:
                    None
                
                d_resp = {'status':'success'}
            else:
                 d_resp = {'status':'failed'}
        return d_resp

    class Meta:
        model = Transactions
        fields = ['orders'] 
 