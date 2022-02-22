from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = {
            'title': 'Об авторе',
            'name': 'Богдан',
            'github': 'https://github.com/bog2530',
        }
        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'
