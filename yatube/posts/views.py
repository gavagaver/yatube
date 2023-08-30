from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post
from .services import add_like, is_liked, remove_like

POST_PER_PAGE: int = 10

User = get_user_model()


def make_paginator(request, post_list):
    """
    Функция для создания объекта пагинатора.

    Аргументы:
    - request (HttpRequest): объект запроса
    - post_list (QuerySet): список постов

    Возвращает:
    - Page: объект страницы пагинации
    """
    paginator = Paginator(post_list, POST_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(20)
def index(request):
    """
    Класс представления главной страницы.

    Аргументы:
    - request (HttpRequest): объект запроса

    Возвращает:
    - HttpResponse: ответ с отображением страницы
    """
    page_obj = make_paginator(
        request,
        Post.objects.select_related('group', 'author').all(),
    )
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """
    Класс представления страницы со списком постов в группе.

    Аргументы:
    - request (HttpRequest): объект запроса
    - slug (str): уникальный идентификатор группы

    Возвращает:
    - HttpResponse: ответ с отображением страницы
    """
    group = get_object_or_404(Group, slug=slug)
    page_obj = make_paginator(
        request,
        group.posts.select_related('author').all(),
    )
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """
    Класс представления страницы профиля пользователя.

    Аргументы:
    - request (HttpRequest): объект запроса
    - username (str): имя пользователя

    Возвращает:
    - HttpResponse: ответ с отображением страницы
    """
    author = get_object_or_404(User, username=username)
    page_obj = make_paginator(
        request,
        author.posts.select_related('group').all()
    )
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author=author,
    ).exists()
    context = {'page_obj': page_obj,
               'author': author,
               'following': following,
               }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """
    Класс представления страницы поста.

    Аргументы:
    - request (HttpRequest): объект запроса
    - post_id (int): идентификатор поста

    Возвращает:
    - HttpResponse: ответ с отображением страницы
    """
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    comments = post.comments.all()
    post_is_liked = is_liked(post, request.user)
    context = {
        'post': post,
        'form': form,
        'comments': comments,
        'post_id': post_id,
        'post_is_liked': post_is_liked,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """
    Класс представления страницы создания поста.

    Аргументы:
    - request (HttpRequest): объект запроса

    Возвращает:
    - HttpResponse: ответ с отображением страницы
    """
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        author = request.user
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', author.username)
    context = {
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    """
    Класс представления страницы редактирования поста.

    Аргументы:
    - request (HttpRequest): объект запроса
    - post_id (int): идентификатор поста

    Возвращает:
    - HttpResponse: ответ с отображением страницы
    """
    edit_post = get_object_or_404(Post, id=post_id)
    if request.user != edit_post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=edit_post,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {'form': form,
               'is_edit': True,
               'post_id': post_id,
               }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    page_obj = make_paginator(
        request,
        Post.objects.filter(author__following__user=request.user).all(),
    )
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def likes_index(request):
    page_obj = make_paginator(
        request,
        Post.objects.filter(likes__user=request.user).all(),
    )
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/like.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(user=request.user, author=author)
    if follower.exists():
        follower.delete()
    return redirect('posts:profile', username=author)


@login_required
def like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    add_like(post, request.user)
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def unlike(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    remove_like(post, request.user)
    return redirect('posts:post_detail', post_id=post_id)
