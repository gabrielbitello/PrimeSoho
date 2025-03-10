from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),  # Página inicial
    path('login/', views.login_view, name='login_view'),  # Página de login
    path('home/', views.home, name='home'),  # Página de home
]
