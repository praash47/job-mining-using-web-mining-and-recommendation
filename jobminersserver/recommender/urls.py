from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register),
    path('login', views.log_in_user),
    path('skills', views.skills),
    path('logout', views.log_out_user),
    path('recommend', views.recommender),
    path('register', views.register),
    path('job', views.job)
]