# posts/views.py
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User

POSTS_NUM = 10


def get_page_context(queryset, request):
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'paginator': paginator,
        'page_number': page_number,
        'page_obj': page_obj,
    }


def index(request):
    context = get_page_context(Post.objects.all(), request)
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all().filter(group=group)
    context = {
        'group': group,
        'posts': posts,
    }
    context.update(get_page_context(group.posts.all(), request))
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    context = {
        'author': author
    }
    context.update(get_page_context(author.posts.all(), request))
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author_name = post.author
    all_posts = Post.objects.filter(author__username=author_name)
    posts_count = Post.objects.filter(author__username=author_name).count
    context = {
        'post': post,
        'posts_count': posts_count,
        'all_posts': all_posts,
        'author_name': author_name
    }
    return render(request, 'posts/post_detail.html', context)


@login_required(login_url="users:login")
def post_create(request):
    form = PostForm(request.POST)
    groups = Group.objects.all()

    if request.method == 'POST':

        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('posts:profile', request.user)

    return render(
        request, 'posts/create_post.html', {'form': form, 'groups': groups}
    )


@login_required(login_url="users:login")
def post_edit(request, post_id):
    post = Post.objects.get(id=post_id)

    if request.method == 'GET':
        if request.user.id is not post.author.id:
            return redirect('posts:post_detail', post_id)
        form = PostForm(instance=post)

    else:
        form = PostForm(request.POST, instance=post)
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html',
                  {'post': post, 'form': form})
