from django.conf import settings
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import IsAuthenticated

class CacheRouter(DefaultRouter):
    def get_urls(self):
        urls = super().get_urls()
        for url in urls:
            if hasattr(url.callback, 'view_class'):
                view_class = url.callback.view_class
                # Only cache if the view requires authentication
                if hasattr(view_class, 'permission_classes') and IsAuthenticated in view_class.permission_classes:
                    # Apply cache_page decorator with vary_on_cookie to respect authentication
                    url.callback = vary_on_cookie(cache_page(settings.CACHE_MIDDLEWARE_SECONDS))(url.callback)
        return urls 