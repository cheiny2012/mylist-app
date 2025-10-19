from django.urls import path
from . import views

urlpatterns = [
    path('', views.entry_list, name='entry_list'),
    path('<int:pk>/', views.entry_detail, name='entry_detail'),
    path('create/', views.entry_create, name='entry_create'),
    path('<int:pk>/update/', views.entry_update, name='entry_update'),
    path('<int:pk>/delete/', views.entry_delete, name='entry_delete'),
    path('tags/', views.tag_list, name='tag_list'),
]