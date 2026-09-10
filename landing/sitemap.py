"""A hand-rolled sitemap.

django.contrib.sitemaps would pull in the sites framework and a SITE_ID for six
static URLs, so the paths are listed here and rendered by templates/sitemap.xml.
Add a route here when you add a public page.
"""
from django.urls import reverse
from django.views.generic import TemplateView


class SitemapView(TemplateView):
    template_name = 'sitemap.xml'
    content_type = 'application/xml'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pages'] = [
            (reverse('landing:index'), '1.0'),
            (reverse('landing:privacy'), '0.4'),
            (reverse('landing:terms'), '0.4'),
            (reverse('landing:cookies'), '0.4'),
            (reverse('landing:refunds'), '0.4'),
            (reverse('landing:accessibility'), '0.4'),
        ]
        return context
