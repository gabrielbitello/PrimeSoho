from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
#get_object_or_404
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login 
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.http import Http404
from .models import Token_Recuperar_Senha
from django.utils import timezone

# Simular armazenamento de tokens (melhor usar um modelo no banco)
password_reset_tokens = {}

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
            return JsonResponse({'success': False, 'message': 'Usuário ou senha inválidos!'})

    # Se for uma requisição GET, apenas renderiza o formulário de login
    return render(request, 'login.html')


def recover_password_view(request, token=None):
    try:
        if request.method == 'POST':
            if token:  
                # 🌟 2️⃣ Se há um token, processa a redefinição de senha 🌟
                try:
                    new_password = request.POST.get('new_password')
                    if not new_password:
                        raise ValueError("Senha vazia recebida!")

                    if token not in password_reset_tokens:
                        raise KeyError("Token inválido ou expirado!")

                    username = Token_Recuperar_Senha.objects.filter(token=token, ativo=True).first().usuario
                    user = User.objects.get(username=username)
                    user.password = make_password(new_password)  # Criptografa a senha nova
                    user.save()
                    Token_Recuperar_Senha.objects.filter(token=token, ativo=True).update(ativo=False, data_utilizacao=timezone.now())
                    send_mail(
                        'Senha Redefinida',
                        'Sua senha foi redefinida com sucesso. Se você não fez isso, entre em contato conosco por: <a href="mailto:vg.bitello@gmail.com">vg.bitello@gmail.com</a>.',
                        settings.DEFAULT_FROM_EMAIL,  
                        [user.email],
                        fail_silently=False,
                    )
                    
                    return JsonResponse({'success': True, 'message': 'Senha redefinida com sucesso!'})

                except KeyError as e:
                    print(f"[ERROR] Erro de token: {str(e)}")
                    return JsonResponse({'success': False, 'message': 'Token inválido ou expirado.'})
                except User.DoesNotExist:
                    print(f"[ERROR] Usuário não encontrado para token: {token}")
                    return JsonResponse({'success': False, 'message': 'Usuário não encontrado.'})
                except Exception as e:
                    print(f"[ERROR] Erro inesperado ao redefinir senha: {str(e)}")
                    return JsonResponse({'success': False, 'message': f'Erro interno: {str(e)}'})

            else:  
                # 🌟 1️⃣ Se não há token, processa o pedido de recuperação 🌟
                try:
                    username = request.POST.get('username')
                    if not username:
                        raise ValueError("Campo de usuário vazio!")

                    user = User.objects.get(username=username)

                    # Gerar e armazenar o token
                    token = get_random_string(length=32)
                    password_reset_tokens[token] = username  # Salvar o token temporariamente

                    # Criar link real de recuperação
                    reset_link = request.build_absolute_uri(reverse('core:recuperar_senha_token', kwargs={'token': token}))

                    # Enviar email com link para resetar senha
                    send_mail(
                        'Recuperação de Senha',
                        f'Clique no link para redefinir sua senha: {reset_link}',
                        settings.DEFAULT_FROM_EMAIL,  
                        [user.email],
                        fail_silently=False,
                    )

                    DataDB = Token_Recuperar_Senha(usuario=username, token=token)
                    DataDB.save()

                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'Erro interno: {str(e)}'})

                return JsonResponse({'success': True, 'message': 'Se o usuário existir, um e-mail foi enviado com instruções para recuperar a senha.'})

        # 🌟 3️⃣ Renderizar página diferente dependendo se há um token 🌟
        if token and Token_Recuperar_Senha.objects.filter(token=token, ativo=True).exists():
            return render(request, 'recuperar_senha.html', {'token': token})
        else:
            raise Http404("Token inválido ou não encontrado.")

    except Exception as e:
        print(f"[CRITICAL] Erro fatal: {str(e)}")


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