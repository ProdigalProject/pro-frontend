from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('profile', views.profile, name='profile'),
    path('login', views.login, name='login'),
    path('login_query', views.login_query, name='login_query'),
    path('signout', views.signout, name='signout'),
    path('create_user', views.create_user, name='create_user'),
    path('signup', views.signup, name='signup'),
    path('search', views.search, name='search'),
    path('tokensignin', views.receive_token, name='tokensignin'),
    path('add_favorite', views.add_favorite, name='add_favorite'),
    path('remove_favorite', views.remove_favorite, name='remove_favorite'),
    path('favorite', views.favorite, name='favorite'),
    path('sector', views.sector, name='sector')
]
