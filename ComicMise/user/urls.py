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
from accounts.views import home

urlpatterns = [
    # path('',views.login, name='login'),
    path('login/', views.Login.as_view(), name='login'),
    path('',home.as_view(), name='home'),
    path('adminDashboard/',views.adminDashboard.as_view(), name='adminDashboard'),
    path('categoryView/',views.categoryView.as_view(), name='categoryView'),
    path('product_list/',views.product_list.as_view(), name='product_list'),
    path('add_product/',views.add_product.as_view(), name='add_product'),
    path('product_detail/',views.product_detail.as_view(), name='product_detail'),
    path('customers_list/',views.customers_list.as_view(), name='customers_list'),
    
]
