from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
#get_object_or_404
from django.template import loader

# View para a página inicial
def index(request):
    return render(request, 'index.html')

# View para a página de login
def login(request):
    return render(request, 'login.html')

# View para a página de home
def home(request):
    return render(request, 'home.html')

def error_404(request, exception):
    tempalte = loader.get_template('errors/404.html')
    return HttpResponse(content=tempalte.render(), content_type='text/html; charset=utf-8', status=404)


def error_500(request):
    tempalte = loader.get_template('errors/500.html')
    return HttpResponse(content=tempalte.render(), content_type='text/html; charset=utf-8', status=500)