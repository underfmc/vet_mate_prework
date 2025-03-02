from django.views.generic import TemplateView


class PrivacyView(TemplateView):
    template_name = 'about/privacy.html'


class TermsView(TemplateView):
    template_name = 'about/terms.html'
