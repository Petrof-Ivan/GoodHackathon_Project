from django.db import models


class Place(models.Model):
    name = models.TextField(verbose_name='Place name')
    code = models.TextField(verbose_name='QR-code')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Place'


class Review(models.Model):
    place = models.ForeignKey('main.Place', on_delete=models.CASCADE, verbose_name='Place')
    text = models.TextField(verbose_name='Review text')
    author = models.TextField(verbose_name='Reviewer name')

    def __str__(self):
        return f'Review by {self.author}'
