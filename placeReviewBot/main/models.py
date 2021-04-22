from django.db import models


class Place(models.Model):
    name = models.TextField(verbose_name='Place name')
    code = models.TextField(verbose_name='QR-code')

    class Meta:
        verbose_name = 'Place'


class Review(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, verbose_name='Place')
    text = models.TextField(verbose_name='Review text')
    author = models.TextField(verbose_name='Reviewer name')
