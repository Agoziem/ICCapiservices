from re import template
from django.shortcuts import render
from .models import *
from ICCapp.models import Subscription
from ICCapp.serializers import SubscriptionSerializer
from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


# get all email addresses
@api_view(['GET'])
def get_subscriptions(request,organization_id):
    try:
        emails = Subscription.objects.filter(organization=organization_id)
        serializer = SubscriptionSerializer(emails, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Subscription.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

# get all emails
@api_view(['GET'])
def get_emails(request, organization_id):
    try:
        emails = Email.objects.filter(organization=organization_id)
        serializer = EmailSerializer(emails, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Email.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# get a single email
@api_view(['GET'])
def get_email(request, email_id):
    try:
        email = Email.objects.get(id=email_id)
        serializer = EmailSerializer(email, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Email.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

# Add an email view
@api_view(['POST'])
def add_email(request, organization_id):
    try:
        name=request.data.get('name')
        email=request.data.get('email')
        subject=request.data.get('subject')
        message=request.data.get('message')
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    try:
        organization = Organization.objects.get(id=organization_id)
        email = Email.objects.create(organization=organization, name=name, email=email, subject=subject, message=message)
        serializer = EmailSerializer(email, many=False)
        general_room_name = 'emailapi'
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            general_room_name,
            {
                'type': 'chat_message',
                'operation':'create',
                'contact': serializer.data
            }
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(str(e))
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
# Update an email view
@api_view(['PUT'])
def update_email(request, email_id):
    try:
        email = Email.objects.get(id=email_id)
        try:
            email.name = request.data.get('name', email.name)
            email.email = request.data.get('email', email.email)
            email.subject = request.data.get('subject', email.subject)
            email.message = request.data.get('message', email.message)
            email.save()
            serializer = EmailSerializer(email, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
    except Email.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

# Delete an email view
@api_view(['DELETE'])
def delete_email(request, email_id):
    try:
        email = Email.objects.get(id=email_id)
        email.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Email.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
def get_responses(request,message_id):
    try:
        email = Email.objects.get(id=message_id)
        responses = EmailResponse.objects.filter(message=email)
        serializer = EmailResponseSerializer(responses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except EmailResponse.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def create_responses(request):
    try:
        print(request.data)
        serializer = EmailResponseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the response
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Email.DoesNotExist:
        return Response({"error": "Email message not found."}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def getsentemails(request):
    try:
        emails = EmailMessage.objects.all()
        serializer = EmailMessageSerializer(emails, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print(str(e))
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def createEmailMessage(request):
    data = request.data
    try:
        sentEmail = EmailMessage.objects.create(
            subject = data.get("subject"),
            body = data.get("body"),
            template = data.get("template",None),
            status = "sent"
        )
        serializer = EmailMessageSerializer(sentEmail, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    

