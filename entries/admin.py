from django.contrib import admin
from .models import Entry, Tag


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'status', 'rating', 'created_at']
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['title', 'user__username']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'color', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'user__username']