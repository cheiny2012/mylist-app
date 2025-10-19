from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Entry, Tag
from .forms import EntryForm, TagForm
from django.http import JsonResponse
from .api_services import AniListAPI
import json

@login_required
def entry_list(request):
    entries = Entry.objects.filter(user=request.user)
    
    category = request.GET.get('category')
    status = request.GET.get('status')
    search = request.GET.get('search')
    
    if category:
        entries = entries.filter(category=category)
    if status:
        entries = entries.filter(status=status)
    if search:
        entries = entries.filter(Q(title__icontains=search) | Q(notes__icontains=search))
    
    stats = {
        'total': Entry.objects.filter(user=request.user).count(),
        'pendiente': Entry.objects.filter(user=request.user, status='pendiente').count(),
        'en_curso': Entry.objects.filter(user=request.user, status='en_curso').count(),
        'terminado': Entry.objects.filter(user=request.user, status='terminado').count(),
        'abandonado': Entry.objects.filter(user=request.user, status='abandonado').count(),
    }
    
    context = {
        'entries': entries,
        'stats': stats,
        'categories': Entry.CATEGORY_CHOICES,
        'statuses': Entry.STATUS_CHOICES,
    }
    return render(request, 'entries/entry_list.html', context)


@login_required
def entry_detail(request, pk):
    entry = get_object_or_404(Entry, pk=pk, user=request.user)
    return render(request, 'entries/entry_detail.html', {'entry': entry})


@login_required
def entry_create(request):
    if request.method == 'POST':
        form = EntryForm(request.POST, user=request.user)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            form.save_m2m()
            messages.success(request, f'¡Entrada "{entry.title}" creada!')
            return redirect('entry_detail', pk=entry.pk)
    else:
        form = EntryForm(user=request.user)
    
    return render(request, 'entries/entry_form.html', {'form': form, 'action': 'Crear'})


@login_required
def entry_update(request, pk):
    entry = get_object_or_404(Entry, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = EntryForm(request.POST, instance=entry, user=request.user)
        if form.is_valid():
            entry = form.save()
            messages.success(request, f'¡Entrada "{entry.title}" actualizada!')
            return redirect('entry_detail', pk=entry.pk)
    else:
        form = EntryForm(instance=entry, user=request.user)
    
    return render(request, 'entries/entry_form.html', {'form': form, 'action': 'Editar', 'entry': entry})


@login_required
def entry_delete(request, pk):
    entry = get_object_or_404(Entry, pk=pk, user=request.user)
    
    if request.method == 'POST':
        title = entry.title
        entry.delete()
        messages.success(request, f'Entrada "{title}" eliminada.')
        return redirect('entry_list')
    
    return render(request, 'entries/entry_confirm_delete.html', {'entry': entry})


@login_required
def tag_list(request):
    tags = Tag.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            tag = form.save(commit=False)
            tag.user = request.user
            tag.save()
            messages.success(request, f'Tag "{tag.name}" creado!')
            return redirect('tag_list')
    else:
        form = TagForm()
    
    return render(request, 'entries/tag_list.html', {'tags': tags, 'form': form})



@login_required
def search_anime(request):
    """Búsqueda de anime desde AniList API"""
    query = request.GET.get('q', '')
    
    if not query or len(query) < 2:
        return JsonResponse({'results': []})
    
    results = AniListAPI.search_anime(query, limit=10)
    return JsonResponse({'results': results})


@login_required
def import_anime(request):
    """Importa un anime de AniList a la lista del usuario"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        anime_data = data.get('anime')
        
        if not anime_data:
            return JsonResponse({'error': 'Datos inválidos'}, status=400)
        
        # Validar que tenga al menos el título
        title = anime_data.get('title', '').strip()
        if not title:
            return JsonResponse({'error': 'El anime debe tener un título'}, status=400)
        
        # Limpiar la descripción de HTML y caracteres especiales
        import re
        description = anime_data.get('description', '')
        if description:
            # Remover HTML
            description = re.sub('<[^<]+?>', '', description)
            # Remover saltos de línea múltiples
            description = re.sub(r'\n\s*\n', '\n\n', description)
            # Limitar longitud
            description = description[:500]
        
        # Obtener el número de episodios
        episodes = anime_data.get('episodes')
        if episodes and episodes > 0:
            progress_total = int(episodes)
        else:
            progress_total = None
        
        # Verificar si ya existe
        existing = Entry.objects.filter(
            user=request.user,
            external_id=str(anime_data.get('external_id', '')),
            external_source='anilist'
        ).first()
        
        if existing:
            return JsonResponse({
                'error': 'Este anime ya está en tu lista',
                'entry_id': existing.id,
                'redirect_url': f'/entries/{existing.id}/'
            }, status=400)
        
        # Crear entrada
        entry = Entry.objects.create(
            user=request.user,
            title=title[:255],  # Limitar longitud del título
            category='anime',
            status='pendiente',
            external_id=str(anime_data.get('external_id', ''))[:100],
            external_source='anilist',
            external_link=anime_data.get('url', '')[:200],
            cover_image=anime_data.get('cover_image', '')[:200],
            notes=description,
            progress_current=0,
            progress_total=progress_total,
            platform='AniList'
        )
        
        messages.success(request, f'¡Anime "{entry.title}" añadido a tu lista!')
        return JsonResponse({
            'success': True,
            'entry_id': entry.id,
            'redirect_url': f'/entries/{entry.id}/'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        import traceback
        print(f"Error al importar anime: {e}")
        print(traceback.format_exc())
        return JsonResponse({'error': f'Error inesperado: {str(e)}'}, status=500)
    

@login_required
def search_anime_page(request):
    """Página de búsqueda de anime"""
    return render(request, 'entries/search_anime.html')