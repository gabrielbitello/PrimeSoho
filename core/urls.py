from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),  # Página inicial
    path('login/', views.login_view, name='login_view'),  # Página de login
    path('home/', views.home, name='home'),  # Página de home
    path("recuperar_senha/", views.recover_password_view, name="recuperar_senha"),  # URL para recuperar senha 
    path("recuperar_senha/<str:token>/", views.recover_password_view, name="recuperar_senha_token"),  # URL para recuperar senha com token
]
