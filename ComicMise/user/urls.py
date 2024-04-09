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
    # path('',views.login, name='login'),
    path('', views.Login.as_view(), name='login'),
    path('logout/',logout.as_view(), name='logout'),
    path('home/',home.as_view(), name='home'),
    path('adminDashboard/',views.adminDashboard.as_view(), name='adminDashboard'),
    path('categoryView/',views.categoryView.as_view(), name='categoryView'),
    path('order_list/', views.order_list.as_view(), name = 'order_list'),
    path('order_detail/<int:order_id>/',views.order_detail.as_view(),name='order_detail'),
    path('order_status_change/<int:order_id>/',views.order_status_change.as_view(),name='order_status_change'),
    path('admin_cancel_order/<int:order_id>/',views.admin_cancel_order.as_view(),name='admin_cancel_order'),
    path('admin_return_decision/<int:order_id>/<str:dec>/',views.admin_return_decision.as_view(), name='admin_return_decision'),
    path('product_list/',views.product_list.as_view(), name='product_list'),
    path('add_product/',views.add_product.as_view(), name='add_product'),
    path('product_detail/',views.product_detail.as_view(), name='product_detail'),
    path('customers_list/',views.customers_list.as_view(), name='customers_list'),
    path('userblock/<int:user_id>/', views.user_block.as_view(), name = 'user_block'),
    path('userunblock/<int:user_id>/', views.user_unblock.as_view(), name = 'user_unblock'),
    path('sales_report/', views.sales_report.as_view(), name = 'sales_report'),

    
]
