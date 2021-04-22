from django.contrib import admin
from .models import Place, Review


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')


@admin.register(Review)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'place', 'text', 'author')
