from django.contrib import admin
from .models import Place, Review
from .forms import PlaceForm, ReviewForm


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')
    form = PlaceForm


@admin.register(Review)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'place', 'text', 'author')
    form = ReviewForm
