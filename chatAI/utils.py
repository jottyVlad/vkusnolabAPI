from django.conf import settings
from django.views.decorators.cache import cache_page
from rest_framework.routers import DefaultRouter

class CacheRouter(DefaultRouter):
    def get_urls(self):
        urls = super().get_urls()
        for url in urls:
            if hasattr(url.callback, 'view_class'):
                # Apply cache_page decorator to the view
                url.callback = cache_page(settings.CACHE_MIDDLEWARE_SECONDS)(url.callback)
        return urls 