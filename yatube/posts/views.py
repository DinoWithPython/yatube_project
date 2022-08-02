from django.conf import settings
from django.shortcuts import get_object_or_404, render

from .models import Group, Post


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.prefetch_related(
        'author')[:settings.COUNT_OF_VISIBLE_POSTS]
    context = {
        'posts': posts
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.prefetch_related('author')[
        :settings.COUNT_OF_VISIBLE_POSTS]
    context = {
        'group': group,
        'posts': posts
    }
    return render(request, template, context)
