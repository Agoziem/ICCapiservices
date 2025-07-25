from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer
from .serializers import CustomerSerializer, CreateCustomerSerializer, UpdateCustomerSerializer
from drf_yasg.utils import swagger_auto_schema


# get all customers
@swagger_auto_schema(
    method="get",
    responses={
        200: CustomerSerializer(many=True),
        404: 'Customers Not Found'
    }
)
@api_view(['GET'])
def getCustomers(request,organization_id):
    try:
        customers = Customer.objects.filter(organization=organization_id)
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        return Response({'message': 'Customers not found'}, status=status.HTTP_404_NOT_FOUND)

# get customer by id
@swagger_auto_schema(
    method="get",
    responses={
        200: CustomerSerializer,
        404: 'Customer Not Found'
    }
)
@api_view(['GET'])
def getCustomer(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
        serializer = CustomerSerializer(customer, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        return Response({'message': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)


# create customer
@swagger_auto_schema(
    method="post",
    request_body=CreateCustomerSerializer,
    responses={
        201: CustomerSerializer,
        400: 'Bad Request'
    }
)
@api_view(['POST'])
def createCustomer(request,organization_id):
    try:
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(organization=organization_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({'message': 'Customer not created'}, status=status.HTTP_400_BAD_REQUEST)


# update customer
@swagger_auto_schema(
    method="put",
    request_body=UpdateCustomerSerializer,
    responses={
        200: CustomerSerializer,
        400: 'Bad Request',
        404: 'Customer Not Found'
    }
)
@api_view(['PUT'])
def updateCustomer(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
        serializer = CustomerSerializer(instance=customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({'message': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
    

# delete customer
@swagger_auto_schema(
    method="delete",
    responses={
        200: 'Customer deleted successfully',
        404: 'Customer Not Found'
    }
)
@api_view(['DELETE'])
def deleteCustomer(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
        customer.delete()
        return Response({'message': 'Customer deleted successfully'}, status=status.HTTP_200_OK)
    except:
        return Response({'message': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)