from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('accounts/', include('accounts.urls')),
    path('sondages/', include('surveys.urls')),
    path('reponses/', include('responses.urls')),
    path('dashboard/', include('surveys.urls_dashboard')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
