from django.shortcuts import render
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema

# get all subscriptions
class SubscriptionPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

@swagger_auto_schema(
    method="get",
    responses={
        200: PaginatedSubscriptionSerializer,
        404: 'Subscriptions Not Found'
    }
)
@api_view(['GET'])
@permission_classes([])
def get_subscriptions(request, organization_id):
    try:
        # Validate organization exists
        organization = Organization.objects.get(id=organization_id)
        subscriptions = Subscription.objects.filter(organization=organization_id).order_by('-date_added')
        
        if not subscriptions.exists():
            return Response({'error': 'No subscriptions found for this organization'}, status=status.HTTP_404_NOT_FOUND)
            
        paginator = SubscriptionPagination()
        result_page = paginator.paginate_queryset(subscriptions, request)
        serializer = SubscriptionSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching subscriptions: {str(e)}")
        return Response({'error': 'An error occurred while fetching subscriptions'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
# get a single subscription
@swagger_auto_schema(
    method="get",
    responses={
        200: SubscriptionSerializer(),
        404: 'Subscription Not Found'
    }
)
@api_view(['GET'])
@permission_classes([])
def get_subscription(request, subscription_id):
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        serializer = SubscriptionSerializer(subscription, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Subscription.DoesNotExist:
        return Response({'error': 'Subscription not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching subscription: {str(e)}")
        return Response({'error': 'An error occurred while fetching subscription'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# Add a subscription view
@swagger_auto_schema(
    method="post",
    request_body=SubscriptionSerializer,
    responses={
        201: SubscriptionSerializer(),
        400: 'Bad Request',
        404: 'Organization Not Found'
    }
)
@api_view(['POST'])
def add_subscription(request, organization_id):
    try:
        # Validate organization exists
        organization = Organization.objects.get(id=organization_id)
        
        # Validate input data using serializer
        serializer = SubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(organization=organization)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error creating subscription: {str(e)}")
        return Response({'error': 'An error occurred during subscription creation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# update a subscription view
@swagger_auto_schema(
    method="put",
    request_body=SubscriptionSerializer,
    responses={
        200: SubscriptionSerializer(),
        400: 'Bad Request',
        404: 'Subscription Not Found'
    }
)
@api_view(['PUT'])
def update_subscription(request, subscription_id):
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        
        # Validate input data using serializer
        serializer = SubscriptionSerializer(instance=subscription, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Subscription.DoesNotExist:
        return Response({'error': 'Subscription not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error updating subscription: {str(e)}")
        return Response({'error': 'An error occurred during subscription update'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# delete a subscription view
@swagger_auto_schema(
    method="delete",
    responses={
        204: 'Subscription deleted successfully',
        404: 'Subscription Not Found'
    }
)
@api_view(['DELETE'])
def delete_subscription(request, subscription_id):
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        subscription.delete()
        return Response({'message': 'Subscription deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Subscription.DoesNotExist:
        return Response({'error': 'Subscription not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error deleting subscription: {str(e)}")
        return Response({'error': 'An error occurred during subscription deletion'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)