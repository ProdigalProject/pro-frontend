from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('profile', views.profile, name='profile'),
    path('login', views.login, name='login'),
    path('login_query', views.login_query, name='login_query'),
    path('create_user', views.create_user, name='create_user'),
    path('signup', views.signup, name='signup'),
    path('search', views.search, name='search'),
    path('tokensignin', views.receive_token, name='tokensignin')
]