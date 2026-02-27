from django.db import models


class Supplier(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'({self.code}) {self.name}'
