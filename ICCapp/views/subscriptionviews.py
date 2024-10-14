from django.shortcuts import render
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

# get all subscriptions
class SubscriptionPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

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
@api_view(['GET'])
def get_subscription(request, subscription_id):
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        serializer = SubscriptionSerializer(subscription, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Subscription.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# Add a subscription view
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
@api_view(['DELETE'])
def delete_subscription(request, subscription_id):
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Subscription.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)