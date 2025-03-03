import os
from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret Key: Sempre altere a chave secreta em produção e nunca deixe em texto claro no código
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'sua_chave_secreta_aqui')

# Ativar ou desativar o modo de depuração
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

# Hosts permitidos para segurança (Evite 'ALLOWED_HOSTS' = ['*'] em produção)
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'seu_dominio.com']

# Adicionando apps da pasta 'apps' automaticamente
INSTALLED_APPS = [
    'django.contrib.admin',  # Administração do Django
    'django.contrib.auth',   # Autenticação
    'django.contrib.contenttypes',  # Tipos de conteúdo
    'django.contrib.sessions',  # Sessões
    'django.contrib.messages',  # Mensagens
    'django.contrib.staticfiles',  # Arquivos estáticos
    'livereload',  # Atualização automática do navegador
]

# Configuração do banco de dados (comentei porque está desativada)
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.mysql',
#        'NAME': os.getenv('DB_NAME', 'mydb'),
#        'USER': os.getenv('DB_USER', 'user'),
#        'PASSWORD': os.getenv('DB_PASSWORD', 'password'),
#        'HOST': os.getenv('DB_HOST', 'localhost'),
#        'PORT': os.getenv('DB_PORT', '5432'),
#    }
#}

# Lista de templates de cada app, buscando recursivamente dentro das subpastas
app_template_dirs = []

# Verificando cada app para encontrar as pastas de templates
for app in os.listdir(BASE_DIR / 'apps'):
    app_template_dir = BASE_DIR / 'apps' / app / 'templates'
    if app_template_dir.exists() and app_template_dir.is_dir():
        app_template_dirs.append(str(app_template_dir))

STATIC_URL = '/static/'  # URL para acesso aos arquivos estáticos

# Diretório onde os arquivos estáticos serão armazenados em produção
STATIC_ROOT = str(BASE_DIR / 'staticfiles')

# Diretórios adicionais para arquivos estáticos no desenvolvimento
STATICFILES_DIRS = [
    str(BASE_DIR / 'apps' / 'static'),  # Adicionando a pasta static dos apps
]

# Arquivos de Mídia
MEDIA_URL = '/media/'  # URL para uploads de arquivos
MEDIA_ROOT = BASE_DIR / 'media'  # Diretório para armazenar os arquivos de mídia

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Para segurança básica
    'django.contrib.sessions.middleware.SessionMiddleware',  # Para gerenciamento de sessões
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # Protege contra CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Gerencia autenticação
    'django.contrib.messages.middleware.MessageMiddleware',  # Gerencia mensagens
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  # Diretório central de templates
        ] + app_template_dirs,  # Adicionando templates de apps
        'APP_DIRS': True,  # Permite que o Django busque templates dentro de apps
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ROOT_URLCONF = 'config.urls'  # Arquivo que vai conter as URLs principais do seu projeto
