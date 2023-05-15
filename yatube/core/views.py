from django.shortcuts import render


def page_not_found(request, exception):
    """
    Класс представления страницы ошибки 404 Page Not Found.

    Аргументы:
    - request (HttpRequest): объект запроса
    - exception (Exception): объект исключения

    Возвращает:
    - HttpResponse: ответ с отображением страницы
    """
    return render(
        request,
        template_name='core/404.html',
        context={'path': request.path},
        status=404,
    )


def csrf_failure(request, reason=''):
    """
    Класс представления страницы ошибки 403 CSRF.

    Аргументы:
    - request (HttpRequest): объект запроса
    - reason (str): причина ошибки

    Возвращает:
    - HttpResponse: ответ с отображением страницы
    """
    return render(
        request,
        template_name='core/403csrf.html',
    )


def server_error(request):
    """
    Класс представления страницы ошибки 500 Internal Server Error.

    Аргументы:
    - request (HttpRequest): объект запроса

    Возвращает:
    - HttpResponse: ответ с отображением страницы
    """
    return render(
        request,
        template_name='core/500.html',
        status=500,
    )


def permission_denied(request, exception):
    """
    Класс представления страницы ошибки 403 Forbidden.

    Аргументы:
    - request (HttpRequest): объект запроса
    - exception (Exception): объект исключения

    Возвращает:
    - HttpResponse: ответ с отображением страницы
    """
    return render(
        request,
        template_name='core/403.html',
        status=403,
    )
