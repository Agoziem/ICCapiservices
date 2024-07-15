from django.shortcuts import render
from .models import *
from ICCapp.models import Organization
from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .Paystack import Paystack
from django.db.models import Count,Sum,Avg

Customer = get_user_model()
# get all payments
@api_view(['GET'])
def get_payments(request, organization_id):
    try:
        orders = Orders.objects.filter(organization=organization_id)
        serializer = PaymentSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Orders.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# get all payments by a user
@api_view(['GET'])
def get_payments_by_user(request, user_id):
    try:
        orders = Orders.objects.filter(customer=user_id)
        total = orders.count()
        serializer = PaymentSerializer(orders, many=True)
        return Response({"orders":serializer.data,"total":total}, status=status.HTTP_200_OK)
    except Orders.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# get a single payment by id
@api_view(['GET'])
def get_payment(request, payment_id):
    try:
        order = Orders.objects.get(id=payment_id)
        serializer = PaymentSerializer(order, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Orders.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# Add a payment to the Organization
@api_view(['POST'])
def add_payment(request, organization_id):
    try:
        Customerid = request.data.get('customerid')
        Amount = request.data.get('total')
        services = request.data.get('services', [])
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    try:
        organization = Organization.objects.get(id=organization_id)
        customer = Customer.objects.get(id=Customerid)
        services = Service.objects.filter(id__in=services)
        order = Orders.objects.create(organization=organization, customer=customer, amount=Amount)
        order.services.add(*services)
        serializer = PaymentSerializer(order, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Organization.DoesNotExist or Customer.DoesNotExist or Service.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)

# verify a payment
@api_view(['POST'])
def verify_payment(request):
    ref = request.data.get('ref')
    if not ref:
        return Response({'error': 'Reference is required'}, status=status.HTTP_400_BAD_REQUEST)
    paystack = Paystack()
    Paymentstatus, data = paystack.verify_payment(ref)
    if Paymentstatus:
        order = Orders.objects.get(reference=ref)
        order.status = 'Completed'
        order.save()
        order_serializer = PaymentSerializer(order)      
        return Response(order_serializer.data, status=status.HTTP_200_OK)
    else:
        order = Orders.objects.get(reference=ref)
        order.status = 'Failed'
        order.save()
        order_serializer = PaymentSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_400_BAD_REQUEST)

# update a payment view
@api_view(['PUT'])
def update_payment(request, payment_id):
    try:
        order = Orders.objects.get(id=payment_id)
        try:
            organization_id = request.data.get('organizationid', order.organization.id)
            Customerid = request.data.get('customerid', order.customer.id)
            Amount = request.data.get('amount', order.amount)
            services = request.data.get('services', order.services.all())
            organization = Organization.objects.get(id=organization_id)
            customer = Customer.objects.get(id=Customerid)
            services = Service.objects.filter(id__in=services)
            order.organization = organization
            order.customer = customer
            order.amount = Amount
            order.services.clear()
            order.services.add(*services)   
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
    except Orders.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

# delete a payment view
@api_view(['DELETE'])
def delete_payment(request, payment_id):
    try:
        order = Orders.objects.get(id=payment_id)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Orders.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

# get the total number of payments and customers
@api_view(['GET'])
def get_payment_count(request, organization_id):
    try:
        orders = Orders.objects.filter(organization=organization_id)
        customers = orders.values('customer__id','customer__username').annotate(Count('customer'), Sum('amount'), Avg('amount'))
        totalorders = orders.count()
        totalcustomers = len(customers)
        return Response({'totalorders': totalorders, 'totalcustomers': totalcustomers,"customers":customers}, status=status.HTTP_200_OK)
    except Orders.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
