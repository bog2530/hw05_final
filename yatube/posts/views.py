from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

LIMIT = 10


def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    post_list = Post.objects.select_related('author')
    paginator = Paginator(post_list, LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    title = 'Профайл пользователя'
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    counter_posts = author.posts.count()
    author_profile = (author and request.user)
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(
            author=author,
            user=request.user).exists()
    )
    context = {
        'title': title,
        'author': author,
        'page_obj': page_obj,
        'counter_posts': counter_posts,
        'author_profile': author_profile,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    user_obj = User.objects.get(username=post.author)
    counter_posts = user_obj.posts.count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'counter_posts': counter_posts,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    title = 'Новый пост'
    template_name = 'posts/create_post.html'
    form = PostForm(request.POST or None)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', new_post.author)
    context = {
        'title': title,
        'form': form,
    }
    return render(request, template_name, context)


@login_required
def post_edit(request, post_id):
    title = 'Редактировать пост'
    template_name = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    author = request.user
    if post.author != author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        post.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'title': title,
        'form': form,
        'is_edit': True,
    }
    return render(request, template_name, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    title = 'Лента моих подписок'
    post = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post, LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(author=author, user=request.user)
        return redirect('posts:profile', username=username)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        Follow, user=request.user, author__username=username,
    ).delete()
    return redirect('posts:profile', username=username)
