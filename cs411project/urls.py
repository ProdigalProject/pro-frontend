"""cs411project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from demo import views
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index, name='index'),
    url(r'^getRandomWord/', views.getRandomWord),
    url(r'^signup',views.signup),
    url(r'^login', views.login),
    url(r'^index', views.index),
    url(r'^chat', views.chat),
    url(r'^authenticate/', views.authenticate),
    url(r'^getMovie/', views.getMovie),
    url(r'^create_user/', views.create_user),
    url(r'^insertMovieRating/', views.insertMovieRating),
    url(r'^deleteMovieRating/', views.deleteMovieRating),
    url(r'^updateMovieRating/', views.updateMovieRating),
    url(r'^recommend/', views.recommend),
    url(r'^predict/', views.predict), 
    url(r'^post/$', views.Post),
    url(r'^messages/$', views.Messages),
    url(r'^temp',views.Temp), 
]
#urlpatterns += patterns('',
#               (r'^static/(?P<path>.*)$', 'django.views.static.serve',
#                 {'document_root': settings.MEDIA_ROOT}),
#              )
