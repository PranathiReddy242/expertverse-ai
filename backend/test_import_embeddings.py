import sys
sys.path.insert(0, '.')
from app.services.embeddings import get_text_response
print('loaded embeddings')
print(get_text_response('Test prompt for local fallback'))
