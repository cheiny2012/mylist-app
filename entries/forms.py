from django import forms
from .models import Entry, Tag


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['title', 'category', 'status', 'platform', 'progress', 'rating', 'notes', 'external_link', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'placeholder': 'Título'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'platform': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'placeholder': 'Netflix, Steam...'}),
            'progress': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'placeholder': 'Ep 12/24'}),
            'rating': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'min': '1', 'max': '10'}),
            'notes': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'rows': '4'}),
            'external_link': forms.URLInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'tags': forms.CheckboxSelectMultiple(),
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