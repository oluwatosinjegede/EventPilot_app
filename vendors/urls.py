from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='vendor_register'),
    path('dashboard/', views.dashboard, name='vendor_dashboard'),
    path('profile/', views.profile, name='vendor_profile'),
]