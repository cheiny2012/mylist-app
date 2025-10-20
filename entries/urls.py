from django.urls import path
from . import views


urlpatterns = [
    path('', views.entry_list, name='entry_list'),
    path('<int:pk>/', views.entry_detail, name='entry_detail'),
    path('<int:pk>/detail-json/', views.entry_detail_json, name='entry_detail_json'),
    path('<int:pk>/update-json/', views.entry_update_json, name='entry_update_json'),
    # path('create/', views.entry_create, name='entry_create'),  # ← COMENTAR O ELIMINAR
    path('<int:pk>/update/', views.entry_update, name='entry_update'),
    path('<int:pk>/delete/', views.entry_delete, name='entry_delete'),
    path('tags/', views.tag_list, name='tag_list'),
    
    # Búsqueda de anime
    path('search/', views.search_anime_page, name='search_anime_page'),
    path('api/search-anime/', views.search_anime, name='search_anime'),
    path('api/import-anime/', views.import_anime, name='import_anime'),
]