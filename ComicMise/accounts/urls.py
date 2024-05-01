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
    path('link_verification/<uidb64>/<token>/',link_verification.as_view(), name = 'link_verification'),
    path('otp/<int:pk>/', otpVerify.as_view(), name='otp'),
    path('resend-otp/<int:pk>/', resend_otp.as_view(), name='resend-otp'),
    
    path('login/', Login.as_view(), name='login'),
    path('logout/',logout.as_view(), name='logout'),

    path('forgotPassword/',forgotPassword.as_view(), name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/',resetpassword_validate.as_view(), name = 'resetpassword_validate'),
    path('resetPassword/',resetPassword.as_view(), name='resetPassword'),
    
    path('userprofile/<str:user_name>/', userProfile.as_view(), name = 'userProfile' ),
    path('userside_order_detail/<int:order_id>/',userside_order_detail.as_view(),name = 'userside_order_detail'),
    path('add_address/', add_address.as_view(), name = 'add_address'),
    path('edit_address/<int:address_id>/', edit_address.as_view(), name = 'edit_address'),
    path('delete_address/<int:address_id>/', delete_address.as_view(), name = 'delete_address'),
    path('cancel_order/<int:order_id>/', cancel_order.as_view(), name = 'cancel_order'),
    path('edit_account_details/<str:user_name>/', edit_account_details.as_view(), name = 'edit_account_details'),
    path('change_password/', change_password.as_view(), name = 'change_password'),
     
]
