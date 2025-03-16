from django.shortcuts import get_object_or_404, render
from .models import Article, Category
from django.core.paginator import Paginator


def post_list(request):
    category = request.GET.get('category')
    if category == 'all' or category is None:
        posts = Article.objects.all().select_related('category')
    else:
        posts = Article.objects.filter(
            category__url_name=category).select_related('category')

    paginator = Paginator(posts, 10)  # Показывать 10 постов на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categories = Category.objects.all()
    context = {
        'page_obj': page_obj,
        'categories': categories,
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
