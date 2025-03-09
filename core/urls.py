from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),  # Página inicial
    path('login/', views.login, name='login'),  # Página de login
    path('home/', views.home, name='home'),  # Página de home
]
