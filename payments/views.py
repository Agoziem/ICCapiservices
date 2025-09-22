from django.shortcuts import render
from .models import *
from products.models import Product
from services.models import Service
from vidoes.models import Video
from ICCapp.models import Organization
from .serializers import PaymentResponseSerializer, PaymentSerializer, VerifyPaymentSerializer, PaymentCountStatsSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .Paystack import Paystack
from django.db.models import Count,Sum,Avg
from drf_yasg.utils import swagger_auto_schema

Customer = get_user_model()
# get all payments
@swagger_auto_schema(
    method="get",
    responses={
        200: PaymentResponseSerializer(many=True),
        404: 'Payments Not Found'
    }
)
@api_view(['GET'])
def get_payments(request, organization_id):
    try:
        # Validate organization exists
        organization = Organization.objects.get(id=organization_id)
        orders = Orders.objects.filter(organization=organization_id)
        
        if not orders.exists():
            return Response([], status=status.HTTP_200_OK)

        serializer = PaymentResponseSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching payments: {str(e)}")
        return Response({'error': 'An error occurred while fetching payments'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# get all payments by a user
@swagger_auto_schema(
    method="get",
    responses={
        200: PaymentResponseSerializer(many=True),
        404: 'Payments Not Found'
    }
)
@api_view(['GET'])
def get_payments_by_user(request, user_id):
    try:
        # Validate customer exists
        customer = Customer.objects.get(id=user_id)
        orders = Orders.objects.filter(customer=user_id)
        
        if not orders.exists():
            return Response([], status=status.HTTP_200_OK)

        serializer = PaymentResponseSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching user payments: {str(e)}")
        return Response({'error': 'An error occurred while fetching user payments'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# get a single payment by id
@swagger_auto_schema(
    method="get",
    responses={
        200: PaymentResponseSerializer(),
        404: 'Payment Not Found'
    }
)
@api_view(['GET'])
def get_payment(request, payment_id):
    try:
        order = Orders.objects.get(id=payment_id)
        serializer = PaymentResponseSerializer(order, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Orders.DoesNotExist:
        return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching payment: {str(e)}")
        return Response({'error': 'An error occurred while fetching payment'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
def get_payment_by_reference(request, reference):
    try:
        order = Orders.objects.get(reference=reference)
        serializer = PaymentResponseSerializer(order, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Orders.DoesNotExist:
        return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching payment by reference: {str(e)}")
        return Response({'error': 'An error occurred while fetching payment'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# Add a payment to the Organization
@swagger_auto_schema(
    method="post",
    request_body=PaymentSerializer,
    responses={
        201: PaymentResponseSerializer(),
        400: 'Bad Request',
        404: 'Not Found'
    }
)
@api_view(['POST'])
def add_payment(request, organization_id):
    # Validate required fields
    try:
        customer = request.data.get('customer')
        amount = request.data.get('amount')
        services = request.data.get('services', [])
        products = request.data.get('products', [])
        videos = request.data.get('videos', [])
        
        if not customer:
            return Response({'error': 'Customer ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not amount:
            return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        print(f"Error parsing payment data: {str(e)}")
        return Response({'error': 'Invalid request data'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Validate entities exist
        organization = Organization.objects.get(id=organization_id)
        customer = Customer.objects.get(id=customer)
        
        # Validate related objects
        services_objs = Service.objects.filter(id__in=services) if services else []
        products_objs = Product.objects.filter(id__in=products) if products else []
        videos_objs = Video.objects.filter(id__in=videos) if videos else []
        
        # Create order
        order = Orders.objects.create(organization=organization, customer=customer, amount=amount)
        
        # Add relationships
        if services_objs:
            order.services.add(*services_objs)
        if products_objs:
            order.products.add(*products_objs)
        if videos_objs:
            order.videos.add(*videos_objs)
            
        order.save()

        serializer = PaymentResponseSerializer(order, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error creating payment: {str(e)}")
        return Response({'error': 'An error occurred during payment creation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# verify a payment
@swagger_auto_schema(
    method="post",
    request_body=VerifyPaymentSerializer,
    responses={
        200: PaymentResponseSerializer(),
        400: 'Bad Request',
        500: 'Internal Server Error'
    }
)
@api_view(['POST'])
def verify_payment(request):
    # Validate input data using VerifyPaymentSerializer
    serializer = VerifyPaymentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        ref = request.data.get('reference')
        customer_id = request.data.get('customer_id')
        
        # Validate customer exists
        customer = Customer.objects.get(id=customer_id)
        
        # Verify payment with Paystack
        paystack = Paystack()
        payment_status, data = paystack.verify_payment(ref)
        
        # Get order by reference
        order = Orders.objects.prefetch_related('services', 'products', 'videos').get(reference=ref)
        
        if payment_status:
            order.status = 'Completed'
            
            # Update services
            if order.services.exists():
                for service in order.services.all():
                    service.number_of_times_bought += 1
                    service.userIDs_that_bought_this_service.add(customer_id)
                    if service.userIDs_whose_services_have_been_completed.filter(id=customer_id).exists():
                        service.userIDs_whose_services_have_been_completed.remove(customer_id)
                    service.save()
            
            # Update products
            if order.products.exists():
                for product in order.products.all():
                    product.number_of_times_bought += 1
                    product.userIDs_that_bought_this_product.add(customer_id)
                    product.save()
            
            # Update videos
            if order.videos.exists():
                for video in order.videos.all():
                    video.number_of_times_bought += 1
                    video.userIDs_that_bought_this_video.add(customer_id)
                    video.save()
            
            order.save()
            order_serializer = PaymentResponseSerializer(order)
            return Response(order_serializer.data, status=status.HTTP_200_OK)
        else:
            order.status = 'Failed'
            order.save()
            order_serializer = PaymentResponseSerializer(order)
            return Response({'error': 'Payment verification failed', 'order': order_serializer.data}, status=status.HTTP_400_BAD_REQUEST)
            
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
    except Orders.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error verifying payment: {str(e)}")
        return Response({'error': 'An error occurred during payment verification'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# update a payment view
@swagger_auto_schema(
    method="put",
    request_body=PaymentSerializer,
    responses={
        200: PaymentResponseSerializer(),
        400: 'Bad Request',
        404: 'Payment Not Found'
    }
)
@api_view(['PUT'])
def update_payment(request, payment_id):
    try:
        order = Orders.objects.get(id=payment_id)
        
        # Extract data with validation
        organization_id = request.data.get('organizationid', order.organization.pk if order.organization else None)
        customerid = request.data.get('customerid', order.customer.pk if order.customer else None)
        amount = request.data.get('amount', order.amount)
        services = request.data.get('services', [])
        products = request.data.get('products', [])
        videos = request.data.get('videos', [])
        
        # Validate entities
        if organization_id:
            organization = Organization.objects.get(id=organization_id)
            order.organization = organization
            
        if customerid:
            customer = Customer.objects.get(id=customerid)
            order.customer = customer
            
        order.amount = amount
        
        # Update relationships
        if services:
            services_objs = Service.objects.filter(id__in=services)
            order.services.clear()
            order.services.add(*services_objs)
            
        if products:
            products_objs = Product.objects.filter(id__in=products)
            order.products.clear()
            order.products.add(*products_objs)
            
        if videos:
            videos_objs = Video.objects.filter(id__in=videos)
            order.videos.clear()
            order.videos.add(*videos_objs)
            
        order.save()

        serializer = PaymentResponseSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Orders.DoesNotExist:
        return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error updating payment: {str(e)}")
        return Response({'error': 'An error occurred during payment update'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# delete a payment view
@swagger_auto_schema(
    method="delete",
    responses={
        204: 'Payment deleted successfully',
        404: 'Payment Not Found'
    }
)
@api_view(['DELETE'])
def delete_payment(request, payment_id):
    try:
        order = Orders.objects.get(id=payment_id)
        order.delete()
        return Response({'message': 'Payment deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Orders.DoesNotExist:
        return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error deleting payment: {str(e)}")
        return Response({'error': 'An error occurred during payment deletion'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# get the total number of payments and customers
@swagger_auto_schema(
    method="get",
    responses={
        200: PaymentCountStatsSerializer(),
        404: 'Payments Not Found'
    }
)
@api_view(['GET'])
def get_payment_count(request, organization_id):
    try:
        # Validate organization exists
        organization = Organization.objects.get(id=organization_id)
        orders = Orders.objects.filter(organization=organization_id)
        
        if not orders.exists():
            return Response({
                'totalorders': 0, 
                'totalcustomers': 0,
                'customers': []
            }, status=status.HTTP_200_OK)
            
        customers = orders.values('customer__id','customer__username').annotate(Count('customer'), Sum('amount'), Avg('amount'))
        totalorders = orders.count()
        totalcustomers = len(customers)
        
        return Response({
            'totalorders': totalorders, 
            'totalcustomers': totalcustomers,
            'customers': customers
        }, status=status.HTTP_200_OK)
        
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching payment statistics: {str(e)}")
        return Response({'error': 'An error occurred while fetching payment statistics'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
