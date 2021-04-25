from django.db import models


class Place(models.Model):
    name = models.TextField(verbose_name='Place name', unique=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Place'


class Review(models.Model):
    place = models.ForeignKey('main.Place', on_delete=models.CASCADE, verbose_name='Place')
    text = models.TextField(verbose_name='Review text')
    author = models.TextField(verbose_name='Reviewer name')
    author_id = models.TextField(verbose_name='Reviewer id', default=0)
    photo = models.BinaryField(verbose_name='Photo', default=None, null=True)
    created_at = models.DateTimeField(verbose_name='Creation time', auto_now_add=True)

    def __str__(self):
        return f'Review by {self.author}'


class SuperUser(models.Model):
    username = models.TextField(verbose_name='Telegram username (like @user)', unique=True)