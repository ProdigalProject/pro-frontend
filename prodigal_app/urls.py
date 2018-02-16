from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('profile', views.profile, name='profile'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('tokensignin', views.receive_token, name='tokensignin')
]