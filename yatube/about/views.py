from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """
    Класс представления страницы "Об авторе".

    :param template_name: Путь шаблона для отображения страницы.
    """
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """
    Класс представления страницы "О технологиях".

    :param template_name: Путь шаблона для отображения страницы.
    """
    template_name = 'about/tech.html'
