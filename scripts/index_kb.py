#!/usr/bin/env python3
"""
Index knowledge base documents for chatbot RAG system
"""
from services.chatbot_rag import ChatbotRAG
import sys
import json
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))


def main():
    """Index knowledge base documents"""
    print("\n" + "="*60)
    print("HealthNexus AI - Knowledge Base Indexing")
    print("="*60 + "\n")

    # Paths
    project_root = Path(__file__).parent.parent
    kb_file = project_root / 'shared' / 'knowledge_base.json'
    index_dir = project_root / 'shared' / 'chat_index'

    # Load knowledge base
    print(f"📚 Loading knowledge base from: {kb_file}")
    with open(kb_file, 'r') as f:
        documents = json.load(f)

    print(f"📄 Found {len(documents)} documents\n")

    # Initialize chatbot (without LLM for indexing)
    print("🔧 Initializing RAG system...")
    chatbot = ChatbotRAG(
        model_path=None,  # No LLM needed for indexing
        index_dir=index_dir
    )

    # Index documents
    print("⚡ Indexing documents...")
    result = chatbot.index_documents(documents)

    if result['status'] == 'success':
        print(f"\n✅ Successfully indexed {result['total_docs']} documents")
        print(f"📊 Embedding dimension: {result['dimension']}")
        print(f"💾 Index saved to: {index_dir}")
        print("\n" + "="*60)
        print("✨ Indexing complete! Chatbot is ready to use.")
        print("="*60 + "\n")
    else:
        print(f"\n❌ Indexing failed: {result.get('message', 'Unknown error')}")
        sys.exit(1)


if __name__ == '__main__':
    main()
