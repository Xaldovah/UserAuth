from django.urls import path
from .views import RegisterView, LoginView, UserDetailView, OrganisationListView, OrganisationDetailView

urlpatterns = [
        path('auth/register', RegisterView.as_view(), name='register'),
        path('auth/login', LoginView.as_view(), name='login'),
        path('api/users/<uuid:user_id>', UserDetailView.as_view(), name='user-detail'),
        path('api/organisations', OrganisationListView.as_view(), name='organisations'),
        path('api/organisations/<uuid:org_id>', OrganisationDetailView.as_view(), name='organisation-detail'),
]
