"""
URL configuration for KSD project.
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from KSD import views as mainView
from Users import views as usrs

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', mainView.Home, name='home'),
    path('predict/', usrs.prediction, name='prediction'),
    path('train/', usrs.Training, name='training'),
    path('model-performance/', usrs.model_performance, name='model-performance'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
