# Created By  : Sunday Ajayi (http://linkedin.com/in/sunday-ajayi)
# Created Date: 01/03/2022


from django.urls import path
from .apis import  *
from rest_framework.routers import DefaultRouter
 
router = DefaultRouter()


router.register('commodity',CommodityViewSet,'commodity')
router.register('inventory',InventoryHistoryViewSet, 'inv_history')
router.register('inventory-history',InventoryViewSet,'inv')

urlpatterns = router.urls

urlpatterns += [
    path('create/bulk-order/', TheBulkTransactionCreateView.as_view(), name="bulk_order"),
    # path('create/bulk-lcda/',BulkLcdaCreateView.as_view(), name="bulk_lcda_create"),
    # path('get/souls-bank/report/',Souls_bankReportView.as_view(), name='get_souls_bank_data'),
    # path('bulk-post/souls-bank/',TheBulkSoulsbankCreateView.as_view(), name='bulk-post-souls-bank'),
]