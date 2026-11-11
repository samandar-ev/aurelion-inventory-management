from rest_framework import viewsets
from .models import Product, Client, Order
from .serializers import ProductSerializer, ClientSerializer, OrderSerializer
from .permissions import IsCashier, IsSalesAssociate

# The API is a read-only window onto the catalog and records. Every write goes
# through the web views, which enforce pricing, stock and role rules.


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_archived=False).prefetch_related('variants')
    serializer_class = ProductSerializer
    permission_classes = [IsSalesAssociate]


class ClientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsSalesAssociate]


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Order.objects.prefetch_related('items')
    serializer_class = OrderSerializer
    permission_classes = [IsCashier]
