from django.urls import path
from .views import upload_document, query_documents

urlpatterns = [
    path('upload/', upload_document, name='upload_document'),
    path('query/', query_documents, name='query_documents'),
]