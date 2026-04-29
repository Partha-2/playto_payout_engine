from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MerchantViewSet, PayoutViewSet

router = DefaultRouter()
router.register(r'merchants', MerchantViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('payouts', PayoutViewSet.as_view({'post': 'create', 'get': 'list'})),
    path('merchants/<int:pk>/history', MerchantViewSet.as_view({'get': 'history'})),
]
