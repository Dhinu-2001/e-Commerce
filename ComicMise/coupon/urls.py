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
from accounts.views import home,logout

urlpatterns = [
    path('add_coupon/', views.add_coupon.as_view(), name = 'add_coupon'),
    path('coupon_list/', views.coupon_list.as_view(), name = 'coupon_list'),
    path('coupon_action/<int:coupon_id>', views.coupon_action.as_view(), name = 'coupon_action'),
    path('remove_coupon/', views.remove_coupon.as_view(),name = 'remove_coupon'),
]
