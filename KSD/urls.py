"""
URL configuration for KSD project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views as mainView
from Admins import views as adms
from Users import views as usrs
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',mainView.Base,name="Base"),
    path('Home',mainView.Home,name="Home"),
    path('UserLogin',mainView.UserLogin,name="UserLogin"),
    path("UserRegister", mainView.UserRegister, name="UserRegister"),

    
    path('AdminBase',adms.AdminBase,name="AdminBase"),
    path('AdminHome',adms.AdminHome,name="AdminHome"),
    path('UserDetails',adms.UserDetails,name="UserDetails"),
    path('ActivateUsers/',adms.ActivateUsers,name="ActivateUsers"),
    path('AdminLoginCheck',adms.AdminLoginCheck,name="AdminLoginCheck"),
    path('ModelProgress/',adms.ModelProgress,name="ModelProgress"),

    path('UserBase',usrs.UserBase,name="UserBase"),
    path('UserHome',usrs.UserHome,name="UserHome"),
    path('Training',usrs.Training,name="Training"),
    path('prediction',usrs.prediction,name="prediction"),
    path('UserRegisterActions',usrs.UserRegisterActions,name="UserRegisterActions"),
    path('UserLoginCheck',usrs.UserLoginCheck,name="UserLoginCheck")
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
