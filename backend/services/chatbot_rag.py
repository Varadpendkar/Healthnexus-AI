"""
RAG Chatbot Service for HealthNexus AI
Uses FAISS for vector search and Llama 2 for generation
"""
import os
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

logger = logging.getLogger(__name__)

# Lazy import for llama_cpp
_llama_cpp = None


def get_llama_cpp():
    """Lazy load llama_cpp to allow running without model"""
    global _llama_cpp
    if _llama_cpp is None:
        try:
            from llama_cpp import Llama
            _llama_cpp = Llama
        except ImportError:
            logger.warning("llama-cpp-python not installed")
    return _llama_cpp


class ChatbotRAG:
    """RAG-powered chatbot for health insurance queries"""

    # System prompt for strict RAG behavior
    SYSTEM_PROMPT = """You are the HealthNexus AI Insurance Assistant. You must ONLY use the content found in the "RETRIEVED DOCUMENTS" section. Never invent facts.

If asked something not in the retrieved documents, respond:
"I don't have that information in my knowledge base. Would you like me to help with something else?"

Answer format:
1. Provide a BRIEF direct answer (1-3 sentences)
2. Add "Details" section with supporting evidence from documents
3. Include inline citations like [source:ID]
4. End with a "Sources" list

Keep tone professional, concise, and helpful. Never provide medical advice—only insurance information."""

    def __init__(self,
                 model_path: Optional[Path] = None,
                 index_dir: Optional[Path] = None,
                 embed_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize RAG chatbot

        Args:
            model_path: Path to GGUF model file
            index_dir: Directory containing FAISS index and documents
            embed_model: Sentence transformer model name
        """
        self.model_path = model_path
        self.index_dir = index_dir or Path("shared/chat_index")
        self.docs_json = self.index_dir / "docs.json"
        self.index_file = self.index_dir / "faiss.index"

        # Initialize embedding model
        logger.info(f"Loading embedding model: {embed_model}")
        self.embed_model = SentenceTransformer(embed_model)

        # Load documents and index
        self.documents = []
        self.index = None
        self._load_documents()
        self._load_index()

        # Initialize LLM (lazy)
        self.llm = None
        if model_path and model_path.exists():
            self._load_llm()

    def _load_documents(self):
        """Load indexed documents from JSON"""
        if not self.docs_json.exists():
            logger.warning(f"Documents file not found: {self.docs_json}")
            return

        with open(self.docs_json, 'r') as f:
            self.documents = json.load(f)

        logger.info(f"Loaded {len(self.documents)} documents")

    def _load_index(self):
        """Load FAISS index"""
        if not self.index_file.exists():
            logger.warning(f"FAISS index not found: {self.index_file}")
            return

        self.index = faiss.read_index(str(self.index_file))
        logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")

    def _load_llm(self):
        """Load LLM model"""
        Llama = get_llama_cpp()
        if Llama is None:
            logger.error("Cannot load LLM - llama-cpp-python not available")
            return

        try:
            logger.info(f"Loading LLM from: {self.model_path}")
            self.llm = Llama(
                model_path=str(self.model_path),
                n_ctx=2048,
                n_threads=4,
                n_gpu_layers=-1,  # Use Metal acceleration
                verbose=False
            )
            logger.info("✅ LLM loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load LLM: {e}")
            self.llm = None

    def index_documents(self, documents: List[Dict[str, Any]]) -> Dict:
        """
        Index documents for retrieval

        Args:
            documents: List of dicts with 'id', 'text', 'url', 'metadata'

        Returns:
            Status dict
        """
        if not documents:
            return {'status': 'error', 'message': 'No documents provided'}

        # Create index directory
        self.index_dir.mkdir(parents=True, exist_ok=True)

        # Extract texts and embed
        texts = [doc['text'] for doc in documents]
        logger.info(f"Embedding {len(texts)} documents...")
        embeddings = self.embed_model.encode(texts, show_progress_bar=True)

        # Build FAISS index
        dimension = embeddings.shape[1]
        # Inner product (cosine similarity)
        index = faiss.IndexFlatIP(dimension)

        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        index.add(embeddings)

        # Save index and documents
        faiss.write_index(index, str(self.index_file))
        with open(self.docs_json, 'w') as f:
            json.dump(documents, f, indent=2)

        self.index = index
        self.documents = documents

        logger.info(f"✅ Indexed {len(documents)} documents")

        return {
            'status': 'success',
            'total_docs': len(documents),
            'dimension': dimension
        }

    def retrieve(self,
                 query: str,
                 top_k: int = 5,
                 page_context: Optional[str] = None) -> List[Dict]:
        """
        Retrieve relevant documents for query

        Args:
            query: User query
            top_k: Number of documents to retrieve
            page_context: Current page context for boosting relevance

        Returns:
            List of retrieved documents with scores
        """
        if self.index is None or not self.documents:
            return []

        # Embed query
        query_embedding = self.embed_model.encode([query])
        faiss.normalize_L2(query_embedding)

        # Search
        scores, indices = self.index.search(query_embedding, top_k * 2)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.documents):
                continue

            doc = self.documents[idx]
            final_score = float(score)

            # Boost score if page context matches
            if page_context and doc.get('metadata', {}).get('page_type') == page_context:
                final_score *= 1.15

            results.append({
                'id': doc['id'],
                'text': doc['text'],
                'url': doc.get('url', ''),
                'score': final_score,
                'metadata': doc.get('metadata', {})
            })

        # Sort by boosted score and take top_k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]

    def generate_answer(self,
                        query: str,
                        retrieved_docs: List[Dict],
                        conversation_history: Optional[List[Dict]] = None,
                        user_profile: Optional[Dict] = None) -> Dict:
        """
        Generate answer using LLM

        Args:
            query: User query
            retrieved_docs: Retrieved documents
            conversation_history: Previous messages
            user_profile: User profile for personalization

        Returns:
            Dict with answer, sources, metadata
        """
        if not self.llm:
            # Fallback without LLM
            return self._fallback_answer(query, retrieved_docs)

        # Build prompt
        prompt = self._build_prompt(
            query,
            retrieved_docs,
            conversation_history,
            user_profile
        )

        # Generate
        start_time = time.time()
        try:
            response = self.llm(
                prompt,
                max_tokens=512,
                temperature=0.0,
                stop=["</s>", "Human:", "User:"],
                echo=False
            )

            answer = response['choices'][0]['text'].strip()
            latency = time.time() - start_time

            return {
                'answer': answer,
                'sources': [{'id': doc['id'], 'url': doc['url'], 'score': doc['score']}
                            for doc in retrieved_docs],
                'latency_seconds': round(latency, 2),
                'model_info': {
                    'name': 'Llama-2-7B-Chat',
                    'tokens_generated': response['usage']['completion_tokens']
                }
            }

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._fallback_answer(query, retrieved_docs)

    def _build_prompt(self,
                      query: str,
                      retrieved_docs: List[Dict],
                      conversation_history: Optional[List[Dict]] = None,
                      user_profile: Optional[Dict] = None) -> str:
        """Build prompt for LLM"""

        # Format retrieved documents
        docs_text = ""
        for i, doc in enumerate(retrieved_docs, 1):
            docs_text += f"\n[source:{doc['id']}]\n{doc['text']}\n"

        # Format conversation history
        history_text = ""
        if conversation_history:
            for msg in conversation_history[-4:]:  # Last 4 messages
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                history_text += f"\n{role.capitalize()}: {content}\n"

        # Format user profile
        profile_text = ""
        if user_profile:
            age = user_profile.get('age')
            city = user_profile.get('city')
            if age or city:
                profile_text = f"\n\nUser Context: Age {age}, Location: {city}"

        # Build full prompt
        prompt = f"""<s>[INST] <<SYS>>
{self.SYSTEM_PROMPT}
<</SYS>>

RETRIEVED DOCUMENTS:
{docs_text}
{profile_text}

CONVERSATION HISTORY:
{history_text}

USER QUESTION: {query}

Provide a helpful answer with citations. [/INST]"""

        return prompt

    def _fallback_answer(self, query: str, retrieved_docs: List[Dict]) -> Dict:
        """Fallback answer when LLM not available"""

        if not retrieved_docs:
            answer = "I don't have enough information to answer that question."
        else:
            # Return top document snippet
            top_doc = retrieved_docs[0]
            snippet = top_doc['text'][:300] + "..."
            answer = f"Based on available information:\n\n{snippet}\n\n[source:{top_doc['id']}]"

        return {
            'answer': answer,
            'sources': [{'id': doc['id'], 'url': doc['url'], 'score': doc['score']}
                        for doc in retrieved_docs],
            'latency_seconds': 0,
            'model_info': {'name': 'fallback', 'tokens_generated': 0}
        }

    def query(self,
              query: str,
              top_k: int = 5,
              page_context: Optional[str] = None,
              conversation_history: Optional[List[Dict]] = None,
              user_profile: Optional[Dict] = None) -> Dict:
        """
        Main query method - retrieve and generate answer

        Args:
            query: User query
            top_k: Number of documents to retrieve
            page_context: Current page context
            conversation_history: Previous messages
            user_profile: User profile

        Returns:
            Complete response dict
        """
        # Retrieve documents
        retrieved_docs = self.retrieve(query, top_k, page_context)

        # Generate answer
        result = self.generate_answer(
            query,
            retrieved_docs,
            conversation_history,
            user_profile
        )

        return result

    def get_status(self) -> Dict:
        """Get chatbot status"""
        return {
            'status': 'ready' if self.index and self.documents else 'not_ready',
            'index': {
                'total_docs': len(self.documents),
                'indexed': self.index.ntotal if self.index else 0
            },
            'llm': {
                'loaded': self.llm is not None,
                'model_path': str(self.model_path) if self.model_path else None
            }
        }
