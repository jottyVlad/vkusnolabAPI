import django_filters
from django.db.models import Q

from .models import Recipe


class RecipeFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    author = django_filters.NumberFilter(method='filter_author')

    class Meta:
        model = Recipe
        fields = []

    def filter_search(self, queryset, name, value):
        terms = value.split()
        q_objects = Q()

        for term in terms:
            q_objects |= Q(description__icontains=term)
            q_objects |= Q(instructions__icontains=term)
            q_objects |= Q(title__icontains=term)

        return queryset.filter(q_objects)

    def filter_author(self, queryset, name, value):
        return queryset.filter(author__id=value)
