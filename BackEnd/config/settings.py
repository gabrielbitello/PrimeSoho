import os
from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret Key: Sempre altere a chave secreta em produção e nunca deixe em texto claro no código
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'sua_chave_secreta_aqui')

# Ativar ou desativar o modo de depuração
DEBUG = os.getenv('DJANGO_DEBUG', 'Ture') == 'True'

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


# Configuração do banco de dados
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.mysql',  # Engine do banco
#        'NAME': os.getenv('DB_NAME', 'mydb'),  # Nome do banco
#        'USER': os.getenv('DB_USER', 'user'),  # Usuário do banco
#        'PASSWORD': os.getenv('DB_PASSWORD', 'password'),  # Senha
#        'HOST': os.getenv('DB_HOST', 'localhost'),  # Host do banco
#       'PORT': os.getenv('DB_PORT', '5432'),  # Porta do banco
#    }
#}

# Lista de templates de cada app, buscando recursivamente dentro das subpastas
app_template_dirs = []

# Verificando cada app para encontrar as pastas de templates
for app in os.listdir(BASE_DIR / 'apps'):
    app_template_dir = BASE_DIR / 'apps' / app / 'templates'
    if app_template_dir.exists() and app_template_dir.is_dir():
        # Adiciona a pasta de templates do app à lista
        app_template_dirs.append(str(app_template_dir))

# Arquivos Estáticos
STATICFILES_DIRS = [
    BASE_DIR / 'apps' / 'static',  # Diretório global de arquivos estáticos
]

# Agora, vamos garantir que o Django apenas busque um diretório 'static' em cada app
for app in os.listdir(BASE_DIR / 'apps'):
    app_static_dir = BASE_DIR / 'apps' / app / 'static'
    if app_static_dir.exists() and app_static_dir.is_dir():
        STATICFILES_DIRS.append(app_static_dir)

print(f"Static: {STATICFILES_DIRS}\n")

STATIC_URL = '/static/'  # URL para acesso aos arquivos estáticos
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Diretório onde os arquivos estáticos serão armazenados em produção

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
