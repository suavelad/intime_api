from django.db import models
from authentication.models import User
# Create your models here.


# Create your models here.
class Category(models.Model):
    name = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.IntegerField(null=True, blank=True)

class Commodity(models.Model):
    name = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category,on_delete=models.DO_NOTHING,null=True,blank=True,related_name='com_cat')
    type =models.CharField(max_length=20,null=True, blank=True,default='per item')
    unit_price = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User,on_delete=models.DO_NOTHING,null=True,blank=True,related_name='user_com')

    
class Inventory(models.Model):
    name = models.TextField(null=True, blank=True)
    commodity = models.ForeignKey(Commodity,on_delete=models.DO_NOTHING,null=True,blank=True,related_name='inv_com')
    initial_quantity = models.FloatField(null=True, blank=True)
    quantity_used = models.FloatField(null=True, blank=True)
    quantity_left = models.FloatField(null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User,on_delete=models.DO_NOTHING,null=True,blank=True,related_name='user_inv')

class InventoryHistory(models.Model):
    commodity = models.ForeignKey(Commodity,on_delete=models.DO_NOTHING,null=True,blank=True,related_name='inv_his_com')
    initial_quantity = models.FloatField(null=True, blank=True)
    quantity_added = models.FloatField(null=True, blank=True)
    quantity_left = models.FloatField(null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User,on_delete=models.DO_NOTHING,null=True,blank=True,related_name='user_inv_his')



class Transactions(models.Model):
    The_status = (
        ('success','Successful'),
        ('failed','Failure'),
        ('pending','Pending'),
    )
    id = models.AutoField(primary_key=True)
    commodity = models.ForeignKey(Commodity,on_delete=models.DO_NOTHING,null=True,blank=True,related_name='tranc_com')
    vendor = models.ForeignKey(User,on_delete=models.DO_NOTHING,null=True,blank=True,related_name='ven_tranc')
    quantity = models.FloatField(null=True, blank=True)
    unit_price = models.FloatField(null=True, blank=True)
    payment_status = models.CharField(max_length=10,null=True, blank=True,choices=The_status)
    amount = models.FloatField(null=True, blank=True)
    ref = models.CharField(max_length=20,null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING,null=True,blank=True,related_name='user_tranc')


