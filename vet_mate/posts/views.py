from django.shortcuts import get_object_or_404, render
from .models import Article, Category, Tag
from django.core.paginator import Paginator
from django.db.models import Count


def post_list(request):
    category = request.GET.get('category')
    tags = request.GET.getlist('tags')  # Получаем список тегов

    # Фильтрация по категории
    if category == 'all' or category is None:
        posts = Article.objects.all().select_related('category')
    else:
        posts = Article.objects.filter(
            category__url_name=category).select_related('category')

    # Фильтрация и сортировка по тегам
    if tags:
        posts = posts.filter(tags__url_name__in=tags).annotate(
            num_tags=Count('tags')).order_by(
                '-num_tags', '-created_at').distinct()

    paginator = Paginator(posts, 10)  # Показывать 10 постов на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categories = Category.objects.all()
    all_tags = Tag.objects.all()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'tags': all_tags,
        'selected_tags': tags,
        'category': category,
    }
    return render(request, 'posts/post_list.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Article, id=post_id)
    category = request.GET.get('category')
    context = {
        'post': post,
        'category': category,
    }
    return render(request, 'posts/post_detail.html', context)
