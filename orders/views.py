from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import OrderSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication

class OrderCreateView(APIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            # Calculate the total price (example: product price * quantity)
            product = serializer.validated_data['product']
            quantity = serializer.validated_data['quantity']
            total_price = product.price * quantity  # Assuming 'price' field in Product model

            order = serializer.save(user=request.user, total_price=total_price)
            
            # Send email confirmation
            user_email = request.user.email
            order_details = f"Order ID: {order.id}\nProduct: {order.product.name}\nQuantity: {order.quantity}\nTotal Price: {order.total_price}\nStatus: {order.status}"
            send_mail(
                subject='Order Confirmation',
                message=f'Thank you for your order!\n\n{order_details}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user_email],
                fail_silently=False,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderListView(APIView):
    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            user_email = request.user.email
            order_details = f"Order ID: {order.id}\nProduct: {order.product.name}\nQuantity: {order.quantity}"
            send_mail(
                subject='Order Confirmation',
                message=f'Thank you for your order!\n\n{order_details}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user_email],
                fail_silently=False,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk, user=self.request.user)
        except Order.DoesNotExist:
            return None

    def get(self, request, pk):
        order = self.get_object(pk)
        if order is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def delete(self, request, pk):
        order = self.get_object(pk)
        if order is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        order.delete()
        return Response({"message": "Order deleted successfully"}, status=status.HTTP_200_OK)