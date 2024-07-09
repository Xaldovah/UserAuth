from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import User, Organisation
from .serializers import UserSerializer, OrganisationSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token = RefreshToken.for_user(user)
        return Response({
            "status": "success",
            "message": "Registration successful",
            "data": {
                "accessToken": str(token.access_token),
                "user": serializer.data
            }
        }, status=status.HTTP_201_CREATED)
    return Response({
        "errors": [{"field": key, "message": value[0]} for key, value in serializer.errors.items()]
    }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(email=email, password=password)
    if user:
        token = RefreshToken.for_user(user)
        return Response({
            "status": "success",
            "message": "Login successful",
            "data": {
                "accessToken": str(token.access_token),
                "user": UserSerializer(user).data
            }
        }, status=status.HTTP_200_OK)
    return Response({
        "status": "Bad request",
        "message": "Authentication failed",
        "statusCode": 401
    }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request, user_id):
    user = User.objects.filter(userId=user_id, organisations__in=request.user.organisations.all()).first()
    if user:
        return Response({
            "status": "success",
            "message": "User record retrieved",
            "data": UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organisations(request):
    organisations = request.user.organisations.all()
    return Response({
        "status": "success",
        "message": "Organisations retrieved",
        "data": {"organisations": OrganisationSerializer(organisations, many=True).data}
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organisation(request, org_id):
    organisation = Organisation.objects.filter(orgId=org_id, users=request.user).first()
    if organisation:
        return Response({
            "status": "success",
            "message": "Organisation record retrieved",
            "data": OrganisationSerializer(organisation).data
        }, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_organisation(request):
    serializer = OrganisationSerializer(data=request.data)
    if serializer.is_valid():
        organisation = serializer.save()
        organisation.users.add(request.user)
        return Response({
            "status": "success",
            "message": "Organisation created successfully",
            "data": OrganisationSerializer(organisation).data
        }, status=status.HTTP_201_CREATED)
    return Response({
        "status": "Bad Request",
        "message": "Client error",
        "statusCode": 400
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_user_to_organisation(request, org_id):
    user_id = request.data.get('userId')
    user = User.objects.filter(userId=user_id).first()
    organisation = Organisation.objects.filter(orgId=org_id, users=request.user).first()
    if user and organisation:
        organisation.users.add(user)
        return Response({
            "status": "success",
            "message": "User added to organisation successfully"
        }, status=status.HTTP_200_OK)
    return Response({
        "status": "Bad Request",
        "message": "Client error",
        "statusCode": 400
    }, status=status.HTTP_400_BAD_REQUEST)
