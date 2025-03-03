from django.urls import path
from . import views

urlpatterns = [
    path('formulario/', views.listar_formularios, name='listar_formularios'),
    path('formulario/<str:folder>/', views.formulario, name='formulario'),
]
