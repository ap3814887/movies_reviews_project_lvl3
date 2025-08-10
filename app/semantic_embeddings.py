from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

model = SentenceTransformer('all-MiniLM-L6-v2')

# Генерация эмбединга из текста
def get_embedding(text: str) -> np.ndarray:
    emb = model.encode([text])[0]
    emb = emb / np.linalg.norm(emb)  # нормализация для косинусного сходства
    return emb.astype('float32')

# Построение FAISS-индекса по списку эмбедингов
def build_faiss_index(embeddings: list[np.ndarray]) -> faiss.IndexFlatL2:
    dim = len(embeddings[0])
    index = faiss.IndexFlatIP(dim)  
    index.add(np.array(embeddings, dtype='float32'))
    return index

# Поиск top-K похожих эмбедингов
def get_top_k_similar(index: faiss.IndexFlatIP, query_embedding: np.ndarray, k: int = 5) -> list[int]:
    query_embedding = query_embedding.reshape(1, -1).astype('float32')
    distances, indices = index.search(query_embedding, k)
    return indices[0].tolist()