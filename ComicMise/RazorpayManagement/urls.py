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
    path('handlerequest/',handlerequest, name = 'handlerequest'),
    path('razorpay_success/<int:order_id>/',razorpay_success,name='razorpay_success'),
    path('razorpay_retry/<int:order_id>/',razorpay_retry,name='razorpay_retry'),
    path('handlerequest_retry/',handlerequest_retry, name = 'handlerequest_retry'),
    path('razorpay_success__retry/<int:order_id>/',razorpay_success__retry,name='razorpay_success__retry'),
    ]
