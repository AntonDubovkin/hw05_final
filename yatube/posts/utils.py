from django.core.paginator import Paginator

COUNT_PAGINATOR = 10


def paginate(posts, request):
    """Функция паджинации"""
    paginator = Paginator(posts, COUNT_PAGINATOR)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
