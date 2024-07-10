from django.contrib import admin
from django.urls import path, include
from backend import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/register', views.register),
    path('auth/login', views.login),
    path('api/users/<uuid:user_id>', views.get_user),
    path('api/organisations', views.get_organisations),
    path('api/organisations/<uuid:org_id>', views.get_organisation),
    path('api/organisations', views.create_organisation),
    path('api/organisations/<uuid:org_id>/users', views.add_user_to_organisation),
]
