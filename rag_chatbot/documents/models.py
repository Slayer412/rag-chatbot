from django.db import models
from pgvector.django import VectorField

class DocumentChunk(models.Model):
    text = models.TextField()
    embedding = VectorField(dimensions=1536)  # Adjust dimensions according to your embedding model