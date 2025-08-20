
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from students_app .views import loginPage
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('students_app.urls', namespace="student")),
    path('admin_app/', include('admin_app.urls', namespace="principal")),
    path('teachers/', include('teachers_app.urls', namespace="teacher")),
    # path("__reload__/", include("django_browser_reload.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
