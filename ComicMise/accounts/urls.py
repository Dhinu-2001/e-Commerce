"""
URL configuration for ComicMise project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.register, name='register'),
    # path('login/',views.login, name='login'),
    path('logout/',views.logout, name='logout'),
    path('home/',views.home, name='home'),
    path('store/',views.store, name='store'),
    path('store/<slug:category_slug>/',views.store, name='products_by_category'),
    path('store/<slug:category_slug>/<slug:product_slug>/',views.product_detail, name='product_detail'),
    path('otp/<int:pk>/', views.otpVerify, name='otp'),
    path('resend-otp/<int:pk>/', views.resend_otp, name='resend-otp'),
]
