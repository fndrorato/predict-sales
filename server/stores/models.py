from django.db import models


class Store(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'({self.code}) {self.name}'
