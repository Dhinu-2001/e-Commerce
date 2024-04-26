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
from .views import *

urlpatterns = [
    path('',store.as_view(), name='store'),
    path('store/category/<slug:category_slug>/',store.as_view(), name='products_by_category'),
    path('store/category/<slug:category_slug>/<slug:product_slug>/<str:size>/',product_detail.as_view(), name='product_detail'),
    path('store/search/',search.as_view(), name='search'),
    path('sort/',sort.as_view(), name='sort'),
]
