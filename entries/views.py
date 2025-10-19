from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Entry, Tag
from .forms import EntryForm, TagForm


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