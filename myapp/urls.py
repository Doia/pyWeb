from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('snake/', views.snake_game, name='snake_game'),
    path('next_snake_move/', views.next_snake_move, name='next_snake_move'),
    path('next_snake_gen/', views.next_snake_gen, name='next_snake_gen'),
]

