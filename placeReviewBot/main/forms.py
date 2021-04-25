from django import forms

from .models import Place, Review


class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ('name',)
        widgets = {
            'name': forms.TextInput,
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('author', 'text', 'author_id')
        widgets = {
            'author': forms.TextInput,
        }
