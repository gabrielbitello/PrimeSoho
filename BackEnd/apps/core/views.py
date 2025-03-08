from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

# View para a página inicial
def home(request):
    return render(request, 'home.html')

# View para a página de login
def login(request):
    return render(request, 'login.html')

def receber_log(request):
    if request.method == 'POST':
        log_data = request.body
        log = log_data.get('log')
        # Aqui você pode armazenar os logs no banco de dados ou fazer o que quiser com eles
        print(f"Log recebido: {log}")
        return JsonResponse({'status': 'sucesso'}, status=200)
    
    return JsonResponse({'status': 'erro', 'message': 'Método não permitido'}, status=405)