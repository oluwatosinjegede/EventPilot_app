from django.urls import path
from . import views
urlpatterns=[path('', views.organization_list, name='organizations'), path('<int:pk>/', views.organization_detail, name='organization_detail')]