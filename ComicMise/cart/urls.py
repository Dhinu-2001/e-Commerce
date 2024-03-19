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
    path('',cart.as_view(),name='cart'),
    path('add_cart/<int:product>/<int:variant>/',add_cart.as_view(), name='add_cart'),
    path('remove_cart/<int:product>/<int:variant>/',remove_cart.as_view(), name= 'remove_cart'),
    path('remove_cart_item/<int:product>/<int:variant>/',remove_cart_item.as_view(), name= 'remove_cart_item'),
]
