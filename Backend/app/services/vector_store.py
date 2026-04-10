import os
import numpy as np

# Global in-memory store: filename -> list of chunks with their embeddings
# Structure: { "filename.pdf": [ {"chunk_id": 1, "text": "...", "embedding": np.array(...) }, ... ] }
VECTOR_STORE = {}

# Lazy load model
_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading embedding model (lazy load)...")
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Embedding model loaded.")
    return _model

def index_chunks(filename: str, chunks: list):
    """
    Computes embeddings for each chunk and stores them in memory.
    """
    texts = [chunk["text"] for chunk in chunks]
    
    if not texts:
        print(f"No chunks to index for {filename}")
        VECTOR_STORE[filename] = []
        return
        
    print(f"Indexing {len(texts)} chunks for {filename}...")
    model = get_model()
    embeddings = model.encode(texts)
    
    # Associate embeddings with chunks
    stored_chunks = []
    for i, chunk in enumerate(chunks):
        stored_chunks.append({
            "chunk_id": chunk.get("chunk_id", i),
            "text": chunk.get("text", ""),
            "section": chunk.get("section", "general"),
            "embedding": embeddings[i]
        })
        
    VECTOR_STORE[filename] = stored_chunks
    print(f"Indexed {len(stored_chunks)} chunks for {filename}.")

def retrieve_relevant_chunks(filename: str, query: str, top_k: int = 3) -> list:
    """
    Given a query, computes its embedding and returns the top_k most similar chunks from the given filename.
    """
    if filename not in VECTOR_STORE or not VECTOR_STORE[filename]:
        print(f"No chunks found for {filename}")
        return []

    stored_chunks = VECTOR_STORE[filename]
    
    # If there are fewer chunks than top_k, just return all of them
    if len(stored_chunks) <= top_k:
        return stored_chunks
        
    model = get_model()
    query_embedding = model.encode([query])[0]
    
    # Compute cosine similarities using numpy
    chunk_embeddings = np.array([chunk["embedding"] for chunk in stored_chunks])
    
    # Cosine similarity: (A dot B) / (norm(A) * norm(B))
    # sentence-transformers already outputs normalized embeddings, so dot product = cosine similarity
    similarities = np.dot(chunk_embeddings, query_embedding)
    
    # Get top_k indices
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    
    relevant_chunks = [stored_chunks[i] for i in top_indices]
    
    print(f"Retrieved {len(relevant_chunks)} chunks for query: '{query[:50]}...'")
    return relevant_chunks
