import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PyPDF2 import PdfReader
from .models import DocumentChunk
import openai

openai.api_key = 'your_openai_api_key'

@csrf_exempt
def upload_document(request):
    if request.method == 'POST' and request.FILES['document']:
        pdf_file = request.FILES['document']
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"

        # Break the text into smaller chunks (e.g., sentences or paragraphs)
        chunks = text.split('\n')  # Simple chunking by lines
        for chunk in chunks:
            if len(chunk.strip()) > 0:
                embedding = openai.Embedding.create(
                    input=chunk,
                    engine="text-embedding-ada-002"
                )['data'][0]['embedding']
                DocumentChunk.objects.create(text=chunk, embedding=embedding)

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def query_documents(request):
    if request.method == 'POST':
        user_query = request.POST.get('query')
        query_embedding = openai.Embedding.create(
            input=user_query,
            engine="text-embedding-ada-002"
        )['data'][0]['embedding']

        # Retrieve the top 5 most similar chunks
        chunks = DocumentChunk.objects.annotate(
            similarity=F('embedding') @ query_embedding
        ).order_by('-similarity')[:5]

        context = "\n".join([chunk.text for chunk in chunks])
        if not context.strip():
            # Fallback mechanism if no relevant text is found
            prompt = f"Question: {user_query}\nAnswer:"
        else:
            prompt = f"Context: {context}\n\nQuestion: {user_query}\nAnswer:"

        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )

        answer = response.choices[0].text.strip()
        return JsonResponse({'answer': answer})
    return JsonResponse({'status': 'error'}, status=400)