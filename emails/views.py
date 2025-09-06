from django.shortcuts import render,redirect
from .models import *
from ICCapp.models import Subscription, Organization
from ICCapp.serializers import SubscriptionSerializer
from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema

class EmailModulePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


# get all email addresses
@swagger_auto_schema(
    method="get",
    responses={
        200: PaginatedEmailSerializer,
        404: 'Subscriptions Not Found'
    }
)
@api_view(['GET'])
def get_subscriptions(request, organization_id):
    try:
        # Validate organization exists
        organization = Organization.objects.get(id=organization_id)
        emails = Subscription.objects.filter(organization=organization_id)
        
        if not emails.exists():
            return Response({'error': 'No subscriptions found for this organization'}, status=status.HTTP_404_NOT_FOUND)

        paginator = EmailModulePagination()
        result_page = paginator.paginate_queryset(emails, request)
        serializer = SubscriptionSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching subscriptions: {str(e)}")
        return Response({'error': 'An error occurred while fetching subscriptions'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# get all emails
@swagger_auto_schema(
    method="get",
    responses={
        200: PaginatedEmailSerializer,
        404: 'Emails Not Found'
    }
)
@api_view(['GET'])
def get_emails(request, organization_id):
    try:
        # Validate organization exists
        organization = Organization.objects.get(id=organization_id)
        emails = Email.objects.filter(organization=organization_id).order_by("-created_at")
        
        if not emails.exists():
            return Response({'error': 'No emails found for this organization'}, status=status.HTTP_404_NOT_FOUND)

        paginator = EmailModulePagination()
        result_page = paginator.paginate_queryset(emails, request)
        serializer = EmailSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching emails: {str(e)}")
        return Response({'error': 'An error occurred while fetching emails'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# get a single email
@swagger_auto_schema(
    method="get",
    responses={
        200: EmailSerializer,
        404: 'Email Not Found'
    }
)
@api_view(['GET'])
def get_email(request, email_id):
    try:
        email = Email.objects.get(id=email_id)
        serializer = EmailSerializer(email, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Email.DoesNotExist:
        return Response({'error': 'Email not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching email: {str(e)}")
        return Response({'error': 'An error occurred while fetching email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# Add an email view
@swagger_auto_schema(
    method="post",
    request_body=CreateEmailSerializer,
    responses={
        201: EmailSerializer,
        400: 'Bad Request'
    }
)
@api_view(['POST'])
def add_email(request, organization_id):
    # Validate input data using CreateEmailSerializer
    serializer = CreateEmailSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Validate organization exists
        organization = Organization.objects.get(id=organization_id)
        
        # Create email with validated data
        email = serializer.save(organization=organization)
        
        # Send WebSocket notification
        try:
            response_serializer = EmailSerializer(email)
            general_room_name = 'emailapi'
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    general_room_name,
                    {
                        'type': 'chat_message',
                        'operation': 'create',
                        'contact': response_serializer.data
                    }
                )
        except Exception as ws_error:
            print(f"WebSocket notification failed: {str(ws_error)}")
            # Continue execution even if WebSocket fails
        
        return Response(EmailSerializer(email).data, status=status.HTTP_201_CREATED)
        
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error creating email: {str(e)}")
        return Response({'error': 'An error occurred during email creation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# Update an email view
@swagger_auto_schema(
    method="put",
    request_body=UpdateEmailSerializer,
    responses={
        200: EmailSerializer,
        400: 'Bad Request',
        404: 'Email Not Found'
    }
)
@api_view(['PUT'])
def update_email(request, email_id):
    try:
        email = Email.objects.get(id=email_id)
        
        # Validate input data using UpdateEmailSerializer
        serializer = UpdateEmailSerializer(instance=email, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        
        # Return updated email data using EmailSerializer for complete data
        response_serializer = EmailSerializer(email)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
        
    except Email.DoesNotExist:
        return Response({'error': 'Email not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error updating email: {str(e)}")
        return Response({'error': 'An error occurred during email update'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# Delete an email view
@swagger_auto_schema(
    method="delete",
    responses={
        204: 'Email deleted successfully',
        404: 'Email Not Found'
    }
)
@api_view(['DELETE'])
def delete_email(request, email_id):
    try:
        email = Email.objects.get(id=email_id)
        email.delete()
        return Response({'message': 'Email deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Email.DoesNotExist:
        return Response({'error': 'Email not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error deleting email: {str(e)}")
        return Response({'error': 'An error occurred during email deletion'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@swagger_auto_schema(
    method="get",
    responses={
        200: PaginatedEmailResponseSerializer,
        404: 'Email Responses Not Found'
    }
)
@api_view(['GET'])
def get_responses(request, message_id):
    try:
        email = Email.objects.get(id=message_id)
        responses = EmailResponse.objects.filter(message=email)
        
        if not responses.exists():
            return Response({'error': 'No responses found for this email'}, status=status.HTTP_404_NOT_FOUND)

        paginator = EmailModulePagination()
        result_page = paginator.paginate_queryset(responses, request)
        serializer = EmailResponseSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Email.DoesNotExist:
        return Response({'error': 'Email not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching email responses: {str(e)}")
        return Response({'error': 'An error occurred while fetching email responses'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method="post",
    request_body=CreateEmailResponseSerializer,
    responses={
        201: EmailResponseSerializer,
        400: 'Bad Request',
        404: 'Email Not Found',
        500: 'Internal Server Error'
    }
)
@api_view(['POST'])
def create_responses(request):
    # Validate input data using CreateEmailResponseSerializer
    serializer = CreateEmailResponseSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Save the response with validated data
        email_response = serializer.save()
        
        # Return response data using EmailResponseSerializer for complete data
        response_serializer = EmailResponseSerializer(email_response)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
    except Email.DoesNotExist:
        return Response({'error': 'Email message not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error creating email response: {str(e)}")
        return Response({'error': 'An error occurred during email response creation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="get",
    responses={
        200: PaginatedEmailMessageSerializer,
        404: 'No Emails Found'
    }
)
@api_view(['GET'])
def getsentemails(request):
    try:
        emails = EmailMessage.objects.all()
        
        if not emails.exists():
            return Response({'error': 'No sent emails found'}, status=status.HTTP_404_NOT_FOUND)
        paginator = EmailModulePagination()
        result_page = paginator.paginate_queryset(emails, request)
        serializer = EmailMessageSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        print(f"Error fetching sent emails: {str(e)}")
        return Response({'error': 'An error occurred while fetching sent emails'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method="post",
    request_body=CreateEmailMessageSerializer,
    responses={
        201: EmailMessageSerializer,
        400: 'Bad Request',
        500: 'Internal Server Error'
    }
)
@api_view(['POST'])
def createEmailMessage(request):
    # Validate input data using CreateEmailMessageSerializer
    serializer = CreateEmailMessageSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Create email message with validated data and set status
        email_message = serializer.save(status="sent")
        
        # Return created email message data
        response_serializer = EmailMessageSerializer(email_message)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"Error creating email message: {str(e)}")
        return Response({'error': 'An error occurred during email message creation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    

