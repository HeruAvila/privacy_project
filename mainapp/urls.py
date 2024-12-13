from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('us_only/', views.us_only, name='us_only'),
    path('non_us/', views.non_us, name='non_us'),
    path('no_tor/', views.no_tor, name='no_tor'),
]