"""
URL configuration for ComicMise project.

The `urlpatterns` list routes URLs to  For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function     1. Add an import:  from my_app import     2. Add a URL to urlpatterns:  path('', home, name='home')
Class-based     1. Add an import:  from other_app.import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from .views import *

urlpatterns = [
    path('register/',register.as_view(), name='register'),
    path('logout/',logout.as_view(), name='logout'),
    path('home/',home.as_view(), name='home'),
    
    path('otp/<int:pk>/', otpVerify.as_view(), name='otp'),
    path('resend-otp/<int:pk>/', resend_otp.as_view(), name='resend-otp'),
    path('userprofile/<str:user_name>/', userProfile.as_view(), name = 'userProfile' ),
    path('userside_order_detail/<int:order_id>/',userside_order_detail.as_view(),name = 'userside_order_detail'),
    path('cancel_order/<int:order_id>/', cancel_order.as_view(), name = 'cancel_order'),

]
