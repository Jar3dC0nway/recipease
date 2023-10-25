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
]
