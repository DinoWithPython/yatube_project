from django.core.paginator import Paginator
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from .models import Group, Post, User
from .forms import PostForm


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
    user = get_object_or_404(User, username=username)
    user_posts = user.posts.prefetch_related('author')

    paginator = Paginator(user_posts, settings.COUNT_OF_VISIBLE_POSTS)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'author': user,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_id.html'
    post = get_object_or_404(Post, id=int(post_id))
    # post = Post.objects.get(pk=post_id)

    context = {
        'post': post,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            group = form.cleaned_data['group']
            form = form.save(commit=False)
            form.author = request.user
            form.save()
            return redirect('posts:profile', username=request.user)
        return render(request, template, {'form': form})

    form = PostForm()
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=int(post_id))

    if post.author == request.user:
        form = PostForm(request.POST, instance=post)
        if request.method == 'POST' and form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            form.save()
            return redirect('posts:post_detail', post.pk)
        return render(request, template, {'form': form,
                                          'is_edit': True,
                                          'post': post})
    else:
        return redirect('posts:post_detail', post.pk)
