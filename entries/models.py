from django.db import models
from django.conf import settings

class Tag(models.Model):
    """Etiquetas personalizadas para las entradas"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#3B82F6')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tags'
        unique_together = ['user', 'name']
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Entry(models.Model):
    """Entrada principal del usuario"""
    
    CATEGORY_CHOICES = [
        ('anime', '🎬 Anime'),
        ('serie', '📺 Serie'),
        ('pelicula', '🎥 Película'),
        ('manga', '📖 Manga'),
        ('manhwa', '📚 Manhwa'),
        ('libro', '📕 Libro'),
        ('videojuego', '🎮 Videojuego'),
    ]
    
    STATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_curso', 'En Curso'),
        ('terminado', 'Terminado'),
        ('abandonado', 'Abandonado'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='entries')
    tags = models.ManyToManyField(Tag, blank=True, related_name='entries')
    
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendiente')
    
    platform = models.CharField(max_length=100, blank=True)
    progress_current = models.IntegerField(default=0, verbose_name='Progreso actual')
    progress_total = models.IntegerField(null=True, blank=True, verbose_name='Total')
    episodes_count = models.IntegerField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    external_link = models.URLField(blank=True)
    
    external_id = models.CharField(max_length=100, blank=True)
    external_source = models.CharField(max_length=50, blank=True)
    cover_image = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'entries'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"
    
    @property
    def status_badge_color(self):
        colors = {
            'pendiente': 'bg-gray-500',
            'en_curso': 'bg-blue-500',
            'terminado': 'bg-green-500',
            'abandonado': 'bg-red-500',
        }
        return colors.get(self.status, 'bg-gray-500')