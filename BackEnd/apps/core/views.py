from django.shortcuts import render

# View para a página inicial
def home(request):
    return render(request, 'home.html')

# View para a página de login
def login(request):
    return render(request, 'login.html')
