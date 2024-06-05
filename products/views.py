from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import Product
from .serializers import ProductSerializer
from .permissions import IsRetailer, IsCustomerOrReadOnly,IsRetailerOrReadOnly
from rest_framework.permissions import IsAuthenticated, BasePermission
import logging

logger = logging.getLogger(__name__)

class IsRetailer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'retailer'

class IsCustomerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True  # Allow any user to perform safe methods like GET
        return request.user.is_authenticated and request.user.role == 'customer'
class ProductListView(APIView):
    permission_classes = [IsAuthenticated,IsRetailer]

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role != 'retailer':
            return Response({"error": "Retailer permission required"}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated,IsRetailer]

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return None

    def get(self, request, pk):
        product = self.get_object(pk)
        if product is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        if not request.user.is_retailer:
            return Response({"error": "Retailer permission required"}, status=status.HTTP_403_FORBIDDEN)
        product = self.get_object(pk)
        if product is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not request.user.is_retailer:
            return Response({"error": "Retailer permission required"}, status=status.HTTP_403_FORBIDDEN)
        product = self.get_object(pk)
        if product is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        product.delete()
        logger.info(f"Product with id {pk} deleted successfully.")
        return Response({"message": "Product deleted successfully"}, status=status.HTTP_200_OK)
