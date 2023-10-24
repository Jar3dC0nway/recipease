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
]
