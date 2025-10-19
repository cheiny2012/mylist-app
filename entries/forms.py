from django import forms
from .models import Entry, Tag


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['status', 'progress_current', 'progress_total', 'rating', 'notes', 'tags']
        widgets = {
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'progress_current': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'min': '0',
                'placeholder': 'Episodios vistos'
            }),
            'progress_total': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'min': '0',
                'placeholder': 'Total de episodios (opcional)'
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'min': '1',
                'max': '10',
                'placeholder': '1-10'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'rows': '4',
                'placeholder': 'Tus notas personales...'
            }),
            'tags': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'progress_current': 'Episodios vistos',
            'progress_total': 'Total de episodios',
            'rating': 'Calificación (1-10)',
            'notes': 'Notas',
            'tags': 'Etiquetas',
            'status': 'Estado'
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['tags'].queryset = Tag.objects.filter(user=user)


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'w-20 h-10 border rounded cursor-pointer'}),
        }