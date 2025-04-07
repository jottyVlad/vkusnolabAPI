from rest_framework.routers import DefaultRouter

from recipe import views

router = DefaultRouter()

router.register('recipe', views.RecipeViewSet, basename='recipe_viewset')
router.register('ingredients', views.IngredientsViewSet, basename='ingredient_viewset')
router.register('recipe_ingredients', views.RecipeIngredientsViewSet, basename='recipe_ingredients_viewset')

router.register('likes', views.LikesViewSet, basename='likes_viewset')

#router.register('search_history', views.SearchHistoryViewSet, basename='search_viewset')

router.register('comments', views.CommentsViewSet, basename='comments_viewset')
