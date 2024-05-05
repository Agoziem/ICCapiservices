from django.shortcuts import render
from .models import *
from ICCapp.models import Organization
from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


# get all payments
@api_view(['GET'])
def get_payments(request, organization_id):
    try:
        payments = Payment.objects.filter(organization=organization_id)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Payment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# get a single payment
@api_view(['GET'])
def get_payment(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
        serializer = PaymentSerializer(payment, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Payment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# Add a payment view
@api_view(['POST'])
def add_payment(request, organization_id):
    try:
        Customerid = request.data.get('customerid')
        Amount = request.data.get('amount')
        services = request.data.get('services', [])
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    try:
        organization = Organization.objects.get(id=organization_id)
        customer = Customer.objects.get(id=Customerid)
        services = Service.objects.filter(id__in=services)
        payment = Payment.objects.create(organization=organization, customer=customer, amount=Amount)
        payment.services.add(*services)
        serializer = PaymentSerializer(payment, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Organization.DoesNotExist or Customer.DoesNotExist or Service.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    

# update a payment view
@api_view(['PUT'])
def update_payment(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
        try:
            organization_id = request.data.get('organizationid', payment.organization.id)
            Customerid = request.data.get('customerid', payment.customer.id)
            Amount = request.data.get('amount', payment.amount)
            services = request.data.get('services', payment.services.all())
            organization = Organization.objects.get(id=organization_id)
            customer = Customer.objects.get(id=Customerid)
            services = Service.objects.filter(id__in=services)
            payment.organization = organization
            payment.customer = customer
            payment.amount = Amount
            payment.services.clear()
            payment.services.add(*services)   
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
    except Payment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

# delete a payment view
@api_view(['DELETE'])
def delete_payment(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
        payment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Payment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# payment successful view
@api_view(['POST'])
def payment_successful(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
        payment.status = 'Completed'
        payment.save()
        return Response(status=status.HTTP_200_OK)
    except Payment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


# payment failed view
@api_view(['POST'])
def payment_failed(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
        payment.status = 'Failed'
        payment.save()
        return Response(status=status.HTTP_200_OK)
    except Payment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
