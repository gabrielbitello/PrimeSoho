from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),  # Página inicial
    path('login/', views.login, name='login'),  # Página de login
]
