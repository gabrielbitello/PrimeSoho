from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
#get_object_or_404
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login 
from django.views.decorators.cache import cache_page

# View para a página inicial
def index(request):
    return render(request, 'index.html')

# View para a página de login
def login_view(request):  # Mudamos o nome da função para evitar conflito
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        usuario = request.POST.get('username')
        senha = request.POST.get('password')

        print(usuario)
        print(senha)
        print('a')

        user = authenticate(request, username=usuario, password=senha)

        if user is not None:
            login(request, user)  # Agora usamos a função correta do Django
            return redirect('core:home')  # Redireciona para a página inicial após login
        else:
            return HttpResponse('Usuário ou senha inválidos')

    return render(request, 'login.html')


# View para a página de home
def home(request):
    if request.user.is_authenticated:
        return render(request, 'home.html')
    else:
        return HttpResponse('Acesso negado')

def error_404(request, exception):
    tempalte = loader.get_template('errors/404.html')
    return HttpResponse(content=tempalte.render(), content_type='text/html; charset=utf-8', status=404)


def error_500(request):
    tempalte = loader.get_template('errors/500.html')
    return HttpResponse(content=tempalte.render(), content_type='text/html; charset=utf-8', status=500)