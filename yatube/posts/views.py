from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Post, Group, User, Follow
from .utils import paginate


@cache_page(20)
def index(request):
    """Возвращает главную страницу"""
    posts = Post.objects.select_related('author').all()
    context = {
        'page_obj': paginate(posts, request),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Возвращает страницу групп"""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related()
    context = {
        'group': group,
        'page_obj': paginate(posts, request),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Возвращает профайл пользователя"""
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('author').all()
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author=author
    )
    context = {
        'author': author,
        'following': following,
        'page_obj': paginate(posts, request),
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Возвращает детальную информацию о посте"""
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'),
        pk=post_id)
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


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
def post_create(request):
    """Возвращает  создание поста, для залогиненного пользователя"""
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
    if form.is_valid():
        create_post = form.save(commit=False)
        create_post.author = request.user
        create_post.save()
        return redirect('posts:profile', create_post.author)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Возвращает редактирование поста, для залогиненного
    автора поста или предлагает создать пост"""
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, 'posts/create_post.html', {
        'post': post, 'form': form, 'is_edit': True
    })


@login_required
def follow_index(request):
    """получаем посты в которых author связан через модель Follows
    текущим пользователем через request идем в Post, от туда через filter
     в author, далее через select_related (following) в Follow, далее user.
     Находим пользователя с заданным именем - для него ищем обьекты в
     таблицы Follow которые на него ссылаются далее для всех найденых з
     аписей в Follow ищутся связанные с ним авторы,
     а далее все посты которые связаны с автором"""
    posts = Post.objects.filter(author__following__user=request.user)
    context = {'page_obj': paginate(posts, request)}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Получаем всех автров"""
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    """Получаем всех подписанных юзеров и отписываем их"""
    user_follower = get_object_or_404(
        Follow,
        user=request.user,
        author__username=username
    )
    user_follower.delete()
    return redirect('posts:profile', username)
