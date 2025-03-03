import os
import glob
from django.urls import path, include
from importlib import import_module
from django.conf import settings 

# Caminho do diretório principal onde os aplicativos estão
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Procurar todos os arquivos urls.py nas subpastas de cada aplicativo dentro de 'apps'
app_urls_files = glob.glob(os.path.join(project_dir, 'backend', 'apps', '**', 'urls.py'), recursive=True)

# Inicializar a lista de URLs
urlpatterns = []

# Iterar sobre os arquivos encontrados e importar as URLs
for url_file in app_urls_files:
    # Converte o caminho para o formato de módulo Python (substituindo '/' por '.')
    module_path = url_file.replace(os.path.dirname(url_file), 'backend').replace('.py', '').replace(os.sep, '.')
    
    try:
        # Importa o módulo de URLs do aplicativo
        app_urls = import_module(module_path)
        
        # Adiciona as URLs ao urlpatterns
        urlpatterns.append(path('', include(app_urls)))
        
        # Log opcional se DEBUG estiver ativado
        if settings.DEBUG:
            print(f"Importando URLs da pasta: {module_path}\n")
        
    except ImportError as e:
        print(f"Erro ao importar {module_path}: {e}")

# Exemplo de rota principal (você pode adicionar mais URLs aqui)
urlpatterns += [
    path('', include('apps.core.urls')),  # Incluindo URLs do app 'core' como exemplo
    path('', include('apps.juridico.urls')),  # Incluindo URLs do app 'core' como exemplo
]
