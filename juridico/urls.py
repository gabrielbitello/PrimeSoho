from django.urls import path
from . import views
from django.conf.urls.static import static
import os

app_name = 'juridico'

urlpatterns = [
    path('formulario/', views.listar_formularios, name='form_hub'),
    path('formulario/<str:folder>/', views.formulario, name='formulario'),
    path('home/', views.j_home, name='home'),
]

# Adiciona uma URL específica para a pasta output
current_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(current_dir, 'output')
urlpatterns += static('/output/', document_root=output_path)