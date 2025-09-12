from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Customer
from .serializers import CustomerSerializer, CreateCustomerSerializer, UpdateCustomerSerializer
from drf_yasg.utils import swagger_auto_schema
from ICCapp.models import Organization



# get all customers
@swagger_auto_schema(
    method="get",
    responses={
        200: CustomerSerializer(many=True),
        404: 'Customers Not Found'
    }
)
@api_view(['GET'])
@permission_classes([])
def getCustomers(request, organization_id):
    try:
        # Validate organization exists
        organization = Organization.objects.get(id=organization_id)
        customers = Customer.objects.filter(organization=organization_id)
        
        if not customers.exists():
            return Response({'error': 'No customers found for this organization'}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching customers: {str(e)}")
        return Response({'error': 'An error occurred while fetching customers'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# get customer by id
@swagger_auto_schema(
    method="get",
    responses={
        200: CustomerSerializer,
        404: 'Customer Not Found'
    }
)
@api_view(['GET'])
@permission_classes([])
def getCustomer(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
        serializer = CustomerSerializer(customer, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching customer: {str(e)}")
        return Response({'error': 'An error occurred while fetching customer'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
def createCustomer(request, organization_id):
    # Validate input data using CreateCustomerSerializer
    serializer = CreateCustomerSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Validate organization exists
        organization = Organization.objects.get(id=organization_id)
        
        # Create customer with validated data
        customer = serializer.save(organization=organization)
        
        # Return created customer data
        response_serializer = CustomerSerializer(customer)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error creating customer: {str(e)}")
        return Response({'error': 'An error occurred during customer creation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        
        # Validate input data using UpdateCustomerSerializer
        serializer = UpdateCustomerSerializer(instance=customer, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        
        # Return updated customer data using CustomerSerializer for complete data
        response_serializer = CustomerSerializer(customer)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
        
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error updating customer: {str(e)}")
        return Response({'error': 'An error occurred during customer update'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# delete customer
@swagger_auto_schema(
    method="delete",
    responses={
        204: 'Customer deleted successfully',
        404: 'Customer Not Found'
    }
)
@api_view(['DELETE'])
def deleteCustomer(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
        customer.delete()
        return Response({'message': 'Customer deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error deleting customer: {str(e)}")
        return Response({'error': 'An error occurred during customer deletion'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)