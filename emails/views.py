from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

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
        subject=request.data.get('subject', "")
        message=request.data.get('message')
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    try:
        organization = Organization.objects.get(id=organization_id)
        email = Email.objects.create(organization=organization, name=name, email=email, subject=subject, message=message)
        serializer = EmailSerializer(email, many=False)
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
