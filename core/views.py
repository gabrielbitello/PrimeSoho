from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
#get_object_or_404
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login 
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail


# View para a página inicial
def index(request):
    return render(request, 'index.html')

# View para o login
def login_view(request):
    # Caso o usuário já esteja autenticado, redireciona para a página inicial
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        # Obtém os dados do formulário
        usuario = request.POST.get('username')
        senha = request.POST.get('password')

        # Autentica o usuário com as credenciais fornecidas
        user = authenticate(request, username=usuario, password=senha)

        if user is not None:
            # Se o usuário for válido, realiza o login
            login(request, user)

            # Retorna uma resposta JSON indicando sucesso
            return JsonResponse({'success': True, 'message': 'Login realizado com sucesso!'})
        else:
            # Se as credenciais forem inválidas, retorna uma resposta JSON de erro
            print(f'Usuário ou senha inválidos: {usuario} / {senha}')
            print(f'Post: {request.POST}')
            return JsonResponse({'success': False, 'message': 'Usuário ou senha inválidos!'})

    # Se for uma requisição GET, apenas renderiza o formulário de login
    return render(request, 'login.html')


def recover_password_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            # Enviar email com link para resetar senha
            send_mail(
                'Recuperação de Senha',
                'Clique no link para redefinir sua senha: <LINK_DE_RECUPERACAO>',
                'suporte@seusite.com',
                [user.email],
                fail_silently=False,
            )
            return JsonResponse({'success': True, 'message': 'Um email foi enviado para o seu endereço com instruções para recuperar sua senha.'})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Usuário não encontrado. Verifique as informações e tente novamente.'})
    return JsonResponse({'success': False, 'message': 'Requisição inválida.'})

# View para a página de home
@login_required(login_url='/login/')
def home(request):
    return render(request, 'home.html')


def error_404(request, exception):
    tempalte = loader.get_template('errors/404.html')
    return HttpResponse(content=tempalte.render(), content_type='text/html; charset=utf-8', status=404)


def error_500(request):
    tempalte = loader.get_template('errors/500.html')
    return HttpResponse(content=tempalte.render(), content_type='text/html; charset=utf-8', status=500)