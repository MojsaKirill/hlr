"""hlr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.urls import path

from check_phone.decorators import check_recaptcha
from check_phone.views import PhoneView, MyLoginView, RequestsView, RequestView, AcceptView, DeniedView, DownloadView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', PhoneView.as_view()),
    path('requests', RequestsView.as_view()),
    path('request/<int:id>', RequestView.as_view()),
    path('accept/<int:id>', AcceptView.as_view()),
    path('denied/<int:id>', DeniedView.as_view()),
    path('download/<int:id>', DownloadView.as_view()),
]

urlpatterns += [
    path('login/', check_recaptcha(MyLoginView.as_view())),
    path('logout/', auth_views.LogoutView.as_view())
]
