from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    template = 'posts/index.html'
    return render(request, template)

def group_posts(request, slug):
    # return HttpResponse(f'Страничка с группой {slug}...пошла жара!')
    template = 'posts/group_list.html'
    return render(request, template)