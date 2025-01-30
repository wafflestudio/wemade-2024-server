from django.db import models
from person.models import Person

class Card(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type