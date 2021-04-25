from django.contrib import admin
from .models import Place, Review, SuperUser
from .forms import PlaceForm, ReviewForm, SuperUserForm


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    form = PlaceForm


@admin.register(Review)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'place', 'text', 'author', 'author_id', 'photo', 'created_at')
    form = ReviewForm


@admin.register(SuperUser)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('username',)
    form = SuperUserForm
