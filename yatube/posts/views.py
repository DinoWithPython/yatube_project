from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment
from .utils import create_paginator


def index(request):
    posts = Post.objects.prefetch_related('author', 'group')
    page_obj = create_paginator(request, posts)
    return render(request, 'posts/index.html', {'page_obj': page_obj})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.prefetch_related('author')
    page_obj = create_paginator(request, posts)
    return render(request, 'posts/group_list.html', {'group': group,
                                                     'page_obj': page_obj})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    user_posts = user.posts.prefetch_related('group')
    page_obj = create_paginator(request, user_posts)
    return render(request, 'posts/profile.html', {'author': user,
                                                  'page_obj': page_obj, })


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=int(post_id))
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    comments = Comment.objects.prefetch_related('post').filter(post=post_id)
    return render(request, 'posts/post_detail.html', {'post': post, 'form': form, 'comments': comments})


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if request.method == 'POST' and form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', username=request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=int(post_id))
    if post.author != request.user:
        return redirect('posts:post_detail', post.pk)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.method == 'POST' and form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:post_detail', post.pk)
    return render(request, 'posts/create_post.html', {'form': form,
                                                      'is_edit': True,
                                                      'post': post})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=int(post_id))
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)
