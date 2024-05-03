from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer
from .serializers import CustomerSerializer


# get all customers
@api_view(['GET'])
def getCustomers(request):
    customers = Customer.objects.all()
    serializer = CustomerSerializer(customers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# get customer by id
@api_view(['GET'])
def getCustomer(request, pk):
    try:
        customer = Customer.objects.get(id=pk)
        serializer = CustomerSerializer(customer, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        return Response({'message': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)


# create customer
@api_view(['POST'])
def createCustomer(request):
    serializer = CustomerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# update customer
@api_view(['PUT'])
def updateCustomer(request, pk):
    try:
        customer = Customer.objects.get(id=pk)
        serializer = CustomerSerializer(instance=customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({'message': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
    

# delete customer
@api_view(['DELETE'])
def deleteCustomer(request, pk):
    try:
        customer = Customer.objects.get(id=pk)
        customer.delete()
        return Response({'message': 'Customer deleted successfully'}, status=status.HTTP_200_OK)
    except:
        return Response({'message': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)