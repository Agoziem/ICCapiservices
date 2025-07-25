from django.shortcuts import render
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view
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
        200: SubscriptionSerializer(many=True),
        404: 'Subscriptions Not Found'
    }
)
@api_view(['GET'])
def get_subscriptions(request, organization_id):
    try:
        subscriptions = Subscription.objects.filter(organization=organization_id).order_by('-date_added')
        paginator = SubscriptionPagination()
        result_page = paginator.paginate_queryset(subscriptions, request)
        serializer = SubscriptionSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Subscription.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    
# get a single subscription
@swagger_auto_schema(
    method="get",
    responses={
        200: SubscriptionSerializer(),
        404: 'Subscription Not Found'
    }
)
@api_view(['GET'])
def get_subscription(request, subscription_id):
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        serializer = SubscriptionSerializer(subscription, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Subscription.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
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
        organization = Organization.objects.get(id=organization_id)
        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(organization=organization)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
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
        serializer = SubscriptionSerializer(instance=subscription, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Subscription.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

# delete a subscription view
@swagger_auto_schema(
    method="delete",
    responses={
        204: 'No Content',
        404: 'Subscription Not Found'
    }
)
@api_view(['DELETE'])
def delete_subscription(request, subscription_id):
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Subscription.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)