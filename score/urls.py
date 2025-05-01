from django.contrib import admin
from django.urls import path, include
#from .views import homefunc, player_listfunc,player_detailfunc,PlayerCreateView,PlayerDeleteView,PlayerUpdateView
from .views import *

urlpatterns = [
    path('home/', homefunc, name='home'),
    path('player_list/',player_listfunc, name='player_list'),
    path('player_detail/<int:pk>',player_detailfunc,name='player_detail'),
    path('player_create/', PlayerCreateView.as_view(), name='player_create'),
    path('player_delete/<int:pk>',PlayerDeleteView.as_view(), name='player_delete'),
    path('player_update/<int:pk>',PlayerUpdateView.as_view(), name='player_update'),
    path('game_list',game_listfunc,name='game_list'),
    path('game_create',GameCreateView.as_view(), name='game_create'),
    path('game_detail/<uuid:pk>', game_detailfunc, name='game_detail'),
    path('game_detail/<uuid:pk>/round_create/', round_create_view, name='round_create'),
    path('game_detail/round_edit/<int:round_pk>/', round_edit_view, name='round_edit'),
    path('settings/', setting_list, name='setting_list'),
    path('settings/create/', setting_create, name='setting_create'),
    path('settings/<int:pk>/', setting_detail, name='setting_detail'),
    path('settings/<int:pk>/update/', setting_update, name='setting_update'),
    path('settings/<int:pk>/delete/', setting_delete, name='setting_delete'),
    
]