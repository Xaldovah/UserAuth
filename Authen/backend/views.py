from datetime import datetime, timedelta
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.exceptions import ValidationError
from .serializers import UserSerializer, OrganisationSerializer
from .models import Organisation
import jwt
from django.conf import settings

User = get_user_model()

def generate_token(user):
    exp_time = datetime.utcnow() + timedelta(hours=1)
    token = jwt.encode({
        'user_id': str(user.user_id),
        'exp': exp_time
    }, settings.SECRET_KEY, algorithm='HS256')
    return token

class RegisterView(APIView):
    def post(self, request):
        data = request.data
        serializer = UserSerializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return Response({
                "errors": [{"field": k, "message": str(v[0])} for k, v in e.detail.items()]
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        user = serializer.save()
        user.set_password(data['password'])
        user.save()

        org_name = f"{user.first_name}'s Organisation"
        org = Organisation.objects.create(name=org_name)
        org.users.add(user)
        org.save()

        token = generate_token(user)
        return Response({
            'status': 'success',
            'message': 'Registration successful',
            'data': {
                'accessToken': token,
                'user': serializer.data
            }
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            token = generate_token(user)
            serializer = UserSerializer(user)
            return Response({
                'status': 'success',
                'message': 'Login successful',
                'data': {
                    'accessToken': token,
                    'user': serializer.data
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'Bad request',
                'message': 'Authentication failed',
                'statusCode': 401
            }, status=status.HTTP_401_UNAUTHORIZED)

class UserDetailView(RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'user_id'
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            user_id = kwargs.get('user_id')
            user = User.objects.get(pk=user_id)

            if user == request.user or request.user.organisations.filter(users=user).exists():
                serializer = UserSerializer(user)
                return Response({
                    'status': 'success',
                    'message': 'User retrieved successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': 'Forbidden',
                    'message': 'You do not have permission to view this user'
                }, status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response({
                'status': 'Not Found',
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'Error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OrganisationListView(ListCreateAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.organisations.all()

    def perform_create(self, serializer):
        serializer.save(users=[self.request.user])

    def list(self, request, *args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return Response({'detail': 'Authorization header missing'}, status=status.HTTP_401_UNAUTHORIZED)

            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(pk=payload['user_id'])
            self.request.user = user

            return super().list(request, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return Response({'detail': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.DecodeError:
            return Response({'detail': 'Error decoding token'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OrganisationDetailView(RetrieveAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.organisations.all()

    def retrieve(self, request, *args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return Response({'detail': 'Authorization header missing'}, status=status.HTTP_401_UNAUTHORIZED)
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(pk=payload['user_id'])
            self.request.user = user

            return super().retrieve(request, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return Response({'detail': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.DecodeError:
            return Response({'detail': 'Error decoding token'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
