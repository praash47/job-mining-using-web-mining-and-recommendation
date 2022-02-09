from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path("register", views.register),
    path("login", views.log_in_user),
    path("skills", views.skills),
    path("logout", views.log_out_user),
    path("recommend", views.recommender),
    path("job", views.job),
    path("upload_cv", views.upload_cv),
    path("logs/<str:source>/", views.logs),
]

# for uploaded files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
