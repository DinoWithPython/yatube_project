from django.core.paginator import Paginator
from django.conf import settings
from django.shortcuts import get_object_or_404, render
# from django.contrib.auth.decorators import login_required

from .models import Group, Post


# @login_required
def index(request):
    template = 'posts/index.html'
    posts = Post.objects.prefetch_related('author')

    paginator = Paginator(posts, settings.COUNT_OF_VISIBLE_POSTS)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.prefetch_related('author')

    paginator = Paginator(posts, settings.COUNT_OF_VISIBLE_POSTS)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    context = {

    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_id.html'
    context = {

    }
    return render(request, template, context)
