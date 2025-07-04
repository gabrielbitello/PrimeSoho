"""
URL configuration for PrimeSoho project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404, handler500
from core import views
from PrimeSoho import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('j/', include('juridico.urls')),
    path('imoveis/', include('imoveis.urls')),
    path('c/', include('clientes.urls')),
]

#if settings.DEBUG:
    #from debug_toolbar
    #urlpatterns = [
        #path('__debug__/', include(debug_toolbar.urls)),
    #] + urlpatterns

handler404 = views.error_404
handler500 = views.error_500
