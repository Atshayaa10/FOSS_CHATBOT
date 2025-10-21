# openrouter_pinecone_train.py - OpenRouter + Pinecone with Sentence Transformers
import PyPDF2
import json
import re
import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import time
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "foss-cit-knowledge"
EMBEDDING_DIMENSION = 384  # all-MiniLM-L6-v2 dimension

print("🚀 FOSS-CIT Knowledge Base Creator with Sentence Transformers")
print("=" * 60)

# Initialize local embedding model (no API required!)
print("📦 Loading local embedding model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Local embedding model loaded successfully!")

def extract_comprehensive_pdf_text(pdf_path):
    """Extract all text from PDF with better formatting."""
    try:
        print(f"📖 Reading {os.path.basename(pdf_path)}...")
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            full_text = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                
                # Clean up the text
                page_text = re.sub(r'\s+', ' ', page_text)  # Multiple spaces to single
                page_text = re.sub(r'\n+', '\n', page_text)  # Multiple newlines to single
                
                full_text += f"\n--- Page {page_num + 1} ---\n{page_text}"
        
        print(f"✅ Extracted {len(full_text)} characters from {os.path.basename(pdf_path)}")
        return full_text
        
    except Exception as e:
        print(f"❌ Error reading {pdf_path}: {e}")
        return ""

def create_smart_chunks(text, source_name, chunk_size=500, overlap=50):
    """Create intelligent chunks from text."""
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    chunks = []
    current_chunk = ""
    chunk_id = 1
    
    for sentence in sentences:
        # Check if adding this sentence would exceed chunk size
        if len(current_chunk + sentence) > chunk_size and current_chunk:
            # Save current chunk
            chunks.append({
                "id": f"{source_name}_chunk_{chunk_id}",
                "text": current_chunk.strip(),
                "source": source_name,
                "chunk_size": len(current_chunk),
                "chunk_number": chunk_id
            })
            
            # Start new chunk with overlap
            overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
            current_chunk = overlap_text + " " + sentence
            chunk_id += 1
        else:
            current_chunk += " " + sentence if current_chunk else sentence
    
    # Add final chunk
    if current_chunk.strip():
        chunks.append({
            "id": f"{source_name}_chunk_{chunk_id}",
            "text": current_chunk.strip(),
            "source": source_name,
            "chunk_size": len(current_chunk),
            "chunk_number": chunk_id
        })
    
    return chunks

def get_embedding(text):
    """Get embedding using local Sentence Transformer model."""
    try:
        # Use local model - no API calls needed!
        embedding = embedding_model.encode(text).tolist()
        return embedding
    except Exception as e:
        print(f"❌ Error getting embedding: {e}")
        return None

def setup_pinecone():
    """Initialize Pinecone index."""
    try:
        print("🔧 Setting up Pinecone...")
        
        pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # Check if index exists
        if PINECONE_INDEX_NAME not in pc.list_indexes().names():
            print(f"🆕 Creating new index: {PINECONE_INDEX_NAME}")
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=EMBEDDING_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            print("⏳ Waiting for index to be ready...")
            time.sleep(30)
        else:
            print(f"✅ Using existing index: {PINECONE_INDEX_NAME}")
        
        # Connect to index
        index = pc.Index(PINECONE_INDEX_NAME)
        print(f"✅ Connected to Pinecone index with dimension {EMBEDDING_DIMENSION}")
        return index
        
    except Exception as e:
        print(f"❌ Error setting up Pinecone: {e}")
        return None

def fetch_website_data():
    """Fetch comprehensive data from FOSS-CIT website."""
    try:
        print("🌐 Fetching FOSS-CIT website data...")
        
        base_url = "https://fosscit.netlify.app"
        response = requests.get(base_url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = ' '.join(chunk for chunk in chunks if chunk)
        
        print(f"✅ Fetched {len(clean_text)} characters from website")
        return clean_text
        
    except Exception as e:
        print(f"❌ Error fetching website: {e}")
        return ""

def add_chunks_to_pinecone(index, chunks):
    """Add all chunks to Pinecone with embeddings."""
    print(f"🚀 Adding {len(chunks)} chunks to Pinecone...")
    
    batch_size = 100
    success_count = 0
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        vectors_to_upsert = []
        
        for chunk in batch:
            # Get embedding using local model
            embedding = get_embedding(chunk['text'])
            
            if embedding:
                vectors_to_upsert.append({
                    "id": chunk['id'],
                    "values": embedding,
                    "metadata": {
                        "text": chunk['text'],
                        "source": chunk['source'],
                        "chunk_number": chunk.get('chunk_number', 0),
                        "chunk_size": chunk.get('chunk_size', 0)
                    }
                })
                success_count += 1
            else:
                print(f"❌ Failed to get embedding for chunk {chunk['id']}")
        
        # Upsert batch to Pinecone
        if vectors_to_upsert:
            try:
                index.upsert(vectors=vectors_to_upsert)
                print(f"✅ Uploaded batch {i//batch_size + 1} ({len(vectors_to_upsert)} vectors)")
            except Exception as e:
                print(f"❌ Error uploading batch: {e}")
        
        time.sleep(1)  # Rate limiting
    
    print(f"🎉 Successfully added {success_count} chunks to Pinecone!")
    return success_count

def main():
    """Main function to process PDFs and create knowledge base."""
    
    # Setup Pinecone
    index = setup_pinecone()
    if not index:
        print("❌ Cannot proceed without Pinecone connection")
        return
    
    all_chunks = []
    
    # Process PDF files
    pdf_files = [
        ("data/About FOSS-CIT.pdf", "about_foss-cit"),
        ("data/FOSS-CIT SOP.pdf", "foss-cit_sop")
    ]
    
    for pdf_path, source_name in pdf_files:
        if os.path.exists(pdf_path):
            text = extract_comprehensive_pdf_text(pdf_path)
            if text:
                chunks = create_smart_chunks(text, source_name)
                all_chunks.extend(chunks)
                print(f"📝 Created {len(chunks)} chunks from {source_name}")
        else:
            print(f"⚠️ File not found: {pdf_path}")
    
    # Add website data
    website_text = fetch_website_data()
    if website_text:
        website_chunks = create_smart_chunks(website_text, "website_data")
        all_chunks.extend(website_chunks)
        print(f"🌐 Created {len(website_chunks)} chunks from website")
    
    # Add manual knowledge
    manual_knowledge = [
        {
            "id": "foss_founders_1",
            "text": "FOSS-CIT was founded by Dhileepan Thangamanimaran, Sai Adarsh, and Sibi Bose. These three individuals initiated the Free and Open Source Software Community at Chennai Institute of Technology.",
            "source": "manual_entry",
            "chunk_number": 1,
            "chunk_size": 150
        },
        {
            "id": "foss_mission_1", 
            "text": "FOSS-CIT aims to promote open source software development, provide programming education, and build a community of developers interested in contributing to open source projects.",
            "source": "manual_entry",
            "chunk_number": 2,
            "chunk_size": 140
        }
    ]
    
    all_chunks.extend(manual_knowledge)
    print(f"📋 Added {len(manual_knowledge)} manual knowledge entries")
    
    # Save local knowledge base
    print("💾 Saving local knowledge base...")
    with open('complete_knowledge_base.json', 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    
    print(f"📊 Total chunks created: {len(all_chunks)}")
    
    # Add to Pinecone
    success_count = add_chunks_to_pinecone(index, all_chunks)
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎉 KNOWLEDGE BASE CREATION COMPLETE!")
    print("=" * 60)
    print(f"📁 Local file: complete_knowledge_base.json ({len(all_chunks)} chunks)")
    print(f"☁️ Pinecone vectors: {success_count} uploaded successfully")
    print(f"🔍 Embedding model: Sentence Transformers (local, no API costs!)")
    print(f"📡 Vector database: Pinecone ({PINECONE_INDEX_NAME})")
    print("✅ Ready for semantic search!")

if __name__ == "__main__":
    main()