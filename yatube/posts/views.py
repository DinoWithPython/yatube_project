from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse('Это начальная страница, дальше вас ждет боль...')

def group_posts(request, slug):
    return HttpResponse(f'Страничка с группой {slug}...пошла жара!')