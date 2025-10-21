# openrouter_pinecone_bot.py - Enhanced Bot with OpenRouter + Sentence Transformers
import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import time

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "foss-cit-knowledge"
CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-3.5-turbo")

print("🚀 FOSS-CIT Enhanced Bot with OpenRouter + Local Embeddings")
print("=" * 60)

# Initialize OpenRouter client for chat
print("🤖 Initializing OpenRouter for chat responses...")
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# Initialize local embedding model
print("📦 Loading local embedding model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Local embedding model loaded!")

# Initialize Pinecone
try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    pinecone_index = pc.Index(PINECONE_INDEX_NAME)
    print(f"✅ Connected to Pinecone index: {PINECONE_INDEX_NAME}")
    PINECONE_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Pinecone connection failed: {e}")
    print("📝 Falling back to local knowledge base")
    PINECONE_AVAILABLE = False
    pinecone_index = None

# Flask app setup
app = Flask(__name__)
CORS(app)

# Load local knowledge base as fallback
knowledge_base = []
try:
    with open('complete_knowledge_base.json', 'r', encoding='utf-8') as f:
        knowledge_base = json.load(f)
        print(f"📚 Loaded comprehensive knowledge base with {len(knowledge_base)} chunks")
except FileNotFoundError:
    print("⚠️ No local knowledge base found. Run training script first.")
except Exception as e:
    print(f"❌ Error loading knowledge base: {e}")

def get_embedding(text):
    """Get embedding using local Sentence Transformer model."""
    try:
        # Use local model - no API calls needed!
        embedding = embedding_model.encode(text).tolist()
        return embedding
    except Exception as e:
        print(f"❌ Error getting embedding: {e}")
        return None

def search_pinecone(query, top_k=3):
    """Search Pinecone for relevant chunks."""
    if not PINECONE_AVAILABLE or not pinecone_index:
        return []
    
    try:
        # Get query embedding using local model
        query_embedding = get_embedding(query)
        if not query_embedding:
            return []
        
        # Search Pinecone
        results = pinecone_index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        relevant_chunks = []
        for match in results.matches:
            if match.score > 0.6:  # Similarity threshold
                relevant_chunks.append({
                    'text': match.metadata.get('text', ''),
                    'source': match.metadata.get('source', 'unknown'),
                    'score': match.score
                })
        
        print(f"🔍 Pinecone found {len(relevant_chunks)} relevant chunks")
        return relevant_chunks
        
    except Exception as e:
        print(f"❌ Pinecone search error: {e}")
        return []

def search_local_knowledge(query, top_k=3):
    """Search local knowledge base for relevant information."""
    if not knowledge_base:
        return []
    
    query_lower = query.lower()
    relevant_chunks = []
    
    # Simple keyword matching with scoring
    for chunk in knowledge_base:
        text_lower = chunk['text'].lower()
        score = 0
        
        # Count keyword matches
        query_words = query_lower.split()
        for word in query_words:
            if len(word) > 2:  # Skip very short words
                score += text_lower.count(word) * len(word)
        
        if score > 0:
            relevant_chunks.append({
                'text': chunk['text'],
                'source': chunk.get('source', 'local'),
                'score': score
            })
    
    # Sort by score and return top results
    relevant_chunks.sort(key=lambda x: x['score'], reverse=True)
    print(f"📚 Local search found {len(relevant_chunks[:top_k])} relevant chunks")
    return relevant_chunks[:top_k]

def get_ai_response(user_message, context_chunks):
    """Generate AI response using OpenRouter with context."""
    try:
        # Build context from relevant chunks
        context = ""
        if context_chunks:
            context = "Relevant information:\n"
            for i, chunk in enumerate(context_chunks[:3], 1):
                context += f"{i}. {chunk['text']}\n"
            context += "\n"
        
        # Enhanced system prompt
        system_prompt = f"""You are the FOSS-CIT AI Assistant, a helpful chatbot for the Free and Open Source Software Community (FOSS-CIT) at Coimbatore Institute of Technology.

IMPORTANT: You are the FOSS-CIT chatbot, NOT Coimbatore Institute of Technology itself. Always refer to FOSS-CIT as a community/organization, not as the institute.

Your capabilities:
- Answer questions about FOSS-CIT community, open source software, and programming
- Provide career advice and guidance in technology
- Help with programming concepts and learning paths
- Share information about FOSS community activities and projects

Key Information about FOSS-CIT:
- FOSS-CIT was founded by Dhileepan Thangamanimaran, Sai Adarsh, and Sibi Bose
- FOSS-CIT is a community that promotes open source development and programming education
- Located at Coimbatore Institute of Technology (CIT), but FOSS-CIT is the community organization
- Focus on building a community of developers contributing to open source

Tone: Professional, helpful, encouraging, and technically accurate.

When answering, use phrases like "FOSS-CIT community", "our community", or "the FOSS-CIT organization" - not "we at Coimbatore Institute of Technology".

{context}"""

        # Generate response
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"❌ Error getting AI response: {e}")
        return "I apologize, but I'm having trouble generating a response right now. Please try again."

@app.route('/')
def home():
    return """
    <h1>🤖 FOSS-CIT Enhanced AI Assistant</h1>
    <p><strong>Powered by:</strong></p>
    <ul>
        <li>🧠 OpenRouter for intelligent responses</li>
        <li>🔍 Local Sentence Transformers for embeddings</li>
        <li>☁️ Pinecone for semantic vector search</li>
        <li>📚 Comprehensive PDF knowledge base</li>
    </ul>
    <p><a href="/chat.html">Start Chatting →</a></p>
    <p><a href="/health">Check System Status</a></p>
    """

@app.route('/chat.html')
def chat_page():
    """Serve the chat HTML page."""
    return send_from_directory('.', 'chat.html')

@app.route('/health')
def health():
    """Health check endpoint."""
    status = {
        "status": "healthy",
        "openrouter": "connected" if OPENAI_API_KEY else "missing_key",
        "pinecone": "connected" if PINECONE_AVAILABLE else "disconnected",
        "knowledge_base": f"{len(knowledge_base)} chunks loaded",
        "embedding_model": "sentence-transformers (local)"
    }
    return jsonify(status)

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint."""
    try:
        # Check if request has JSON data
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        print(f"💬 User: {user_message}")
        
        # Search for relevant context
        relevant_chunks = []
        
        # Try Pinecone first
        if PINECONE_AVAILABLE:
            relevant_chunks = search_pinecone(user_message)
        
        # Fallback to local search if Pinecone didn't find enough
        if len(relevant_chunks) < 2:
            local_chunks = search_local_knowledge(user_message)
            relevant_chunks.extend(local_chunks)
        
        # Remove duplicates and limit
        seen_texts = set()
        unique_chunks = []
        for chunk in relevant_chunks:
            if chunk['text'] not in seen_texts:
                unique_chunks.append(chunk)
                seen_texts.add(chunk['text'])
                if len(unique_chunks) >= 3:
                    break
        
        # Generate AI response
        response = get_ai_response(user_message, unique_chunks)
        
        print(f"🤖 Assistant: {response[:100]}...")
        
        return jsonify({
            'response': response,
            'sources_used': len(unique_chunks),
            'search_method': 'pinecone' if PINECONE_AVAILABLE else 'local'
        })
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🌐 Starting FOSS-CIT Enhanced Bot Server...")
    print("=" * 60)
    print("🔗 Main interface: http://127.0.0.1:5000")
    print("💬 Chat interface: http://127.0.0.1:5000/chat.html")
    print("📊 Health check: http://127.0.0.1:5000/health")
    print("=" * 60)
    
    app.run(debug=True, host='127.0.0.1', port=5000)