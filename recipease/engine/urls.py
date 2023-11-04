from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from . import views


from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('accounts/', include('allauth.urls')),
    path('logout', LogoutView.as_view(), name="logout"),
    path("search", views.search, name="search"),
    path('profile/<str:owner>', views.view_profile, name="profile"),
   # path('view_recipes/<str:user>', views.view_recipes, name="view_recipes"),
    path("add_recipe", views.add_recipe, name="add_recipe"),
    path('success/', views.success_view, name='success_view'), 
    path('rating_success/', views.rating_success_view, name='rating_success_view'),
    path('rate_recipe/<int:recipe_id>/', views.rate_recipe, name='rate_recipe'),
    path('add_comment/<int:recipe_id>/', views.add_comment, name='add_comment'),
    path('edit_comment/<int:recipe_id>/<int:comment_id>', views.edit_comment_info, name='edit_comment'),
    path('delete_comment/<int:recipe_id>/<int:comment_id>', views.delete_comment_info, name='delete_comment'),
    path('comment_success/', views.comment_success_view, name='comment_success_view'),
    path('comment_edit_success/', views.comment_edit_success_view, name='comment_edit_success_view'),
    path('comment_delete_success/', views.comment_delete_success_view, name='comment_delete_success_view'),
]
