"""
Cohere Embeddings Service for AudioNovel.
Generates embeddings for scripts and enables semantic search via MongoDB Atlas Vector Search.
"""
import os
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Lazy-load Cohere client
_client = None

def _get_client():
    global _client
    if _client is None:
        if not COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY not found in environment variables")
        import cohere
        _client = cohere.Client(COHERE_API_KEY)
    return _client


def generate_embedding(text: str, input_type: str = "search_document") -> Optional[List[float]]:
    """
    Generate an embedding for a single text using Cohere Embed v3.
    
    Args:
        text: The text to embed.
        input_type: "search_document" for indexing, "search_query" for queries.
    
    Returns:
        A list of floats (embedding vector) or None if unavailable.
    """
    if not COHERE_API_KEY:
        print("COHERE_API_KEY not set; skipping embedding generation.")
        return None
    
    try:
        client = _get_client()
        # Truncate very long texts (Cohere has token limits)
        truncated = text[:8000] if len(text) > 8000 else text
        
        response = client.embed(
            texts=[truncated],
            model="embed-english-v3.0",
            input_type=input_type,
            truncate="END"
        )
        return response.embeddings[0]
    except Exception as e:
        print(f"Error generating Cohere embedding: {e}")
        return None


def generate_embeddings_batch(texts: List[str], input_type: str = "search_document") -> List[Optional[List[float]]]:
    """
    Generate embeddings for multiple texts in one API call.
    
    Returns:
        A list of embedding vectors (or None for failed items).
    """
    if not COHERE_API_KEY:
        return [None] * len(texts)
    
    try:
        client = _get_client()
        truncated = [t[:8000] if len(t) > 8000 else t for t in texts]
        
        response = client.embed(
            texts=truncated,
            model="embed-english-v3.0",
            input_type=input_type,
            truncate="END"
        )
        return response.embeddings
    except Exception as e:
        print(f"Error generating Cohere embeddings batch: {e}")
        return [None] * len(texts)


def search_similar(query: str, collection, limit: int = 5, min_score: float = 0.5) -> List[Dict[str, Any]]:
    """
    Perform semantic search using MongoDB Atlas Vector Search.
    
    Requires a vector search index named 'vector_index' on the collection
    with path 'embedding' and numDimensions 1024 (for embed-english-v3.0).
    
    Args:
        query: The search query text.
        collection: PyMongo collection with embeddings stored.
        limit: Max results to return.
        min_score: Minimum similarity score (0-1).
    
    Returns:
        List of matching documents with scores.
    """
    query_embedding = generate_embedding(query, input_type="search_query")
    if query_embedding is None:
        return []
    
    try:
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": limit * 10,
                    "limit": limit
                }
            },
            {
                "$addFields": {
                    "score": {"$meta": "vectorSearchScore"}
                }
            },
            {
                "$match": {
                    "score": {"$gte": min_score}
                }
            },
            {
                "$project": {
                    "embedding": 0  # Don't return the large embedding array
                }
            }
        ]
        
        results = list(collection.aggregate(pipeline))
        for r in results:
            r['_id'] = str(r['_id'])
        return results
    except Exception as e:
        print(f"Error in vector search: {e}")
        return []
