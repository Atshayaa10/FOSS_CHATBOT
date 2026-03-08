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

# Load configuration from JSON
config = {}
try:
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    print("✅ Configuration loaded from config.json")
except FileNotFoundError:
    print("❌ config.json not found. Using defaults.")
    config = {
        "api_config": {"pinecone_index_name": "foss-cit-knowledge", "embedding_dimension": 384, "embedding_model": "all-MiniLM-L6-v2"},
        "file_paths": {"complete_knowledge_base": "complete_knowledge_base.json"},
        "search_config": {"chunk_size": 500, "chunk_overlap": 50},
        "training_data": {"pdf_files": [], "website_url": "", "manual_knowledge": []}
    }

# Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = config["api_config"]["pinecone_index_name"]
EMBEDDING_DIMENSION = config["api_config"]["embedding_dimension"]

print("🚀 FOSS-CIT Knowledge Base Creator with Sentence Transformers")
print("=" * 60)

# Initialize local embedding model (no API required!)
print("📦 Loading local embedding model...")
embedding_model_name = config["api_config"]["embedding_model"]
embedding_model = SentenceTransformer(embedding_model_name)
print(f"✅ Local embedding model loaded successfully: {embedding_model_name}")

def extract_comprehensive_pdf_text(pdf_path):
    """Extract all text from PDF with better formatting."""
    try:
        print(f"📖 Reading {os.path.basename(pdf_path)}...")
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            full_text = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                
                # DON'T collapse newlines - keep structure for table data
                # Only collapse excessive spaces on same line
                lines = page_text.split('\n')
                cleaned_lines = []
                for line in lines:
                    # Collapse multiple spaces within a line
                    cleaned_line = re.sub(r' +', ' ', line.strip())
                    if cleaned_line:  # Skip empty lines
                        cleaned_lines.append(cleaned_line)
                
                page_text = '\n'.join(cleaned_lines)
                full_text += f"\n--- Page {page_num + 1} ---\n{page_text}"
        
        print(f"✅ Extracted {len(full_text)} characters from {os.path.basename(pdf_path)}")
        return full_text
        
    except Exception as e:
        print(f"❌ Error reading {pdf_path}: {e}")
        return ""

def create_smart_chunks(text, source_name, chunk_size=None, overlap=None):
    """Create intelligent chunks from text."""
    if chunk_size is None:
        chunk_size = config["search_config"]["chunk_size"]
    if overlap is None:
        overlap = config["search_config"]["chunk_overlap"]
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

def create_board_member_chunks_from_json(json_path="board_members.json"):
    """Create clean, well-structured board member chunks from the JSON file."""
    print(f"📋 Creating board member chunks from {json_path}...")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            board_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ {json_path} not found")
        return []
    
    chunks = []
    chunk_id = 1
    
    for year_key, year_data in board_data.items():
        year_range = year_data["year"]
        members = year_data["members"]
        year_short = year_range.split("-")[0].strip()
        
        # --- Chunk 1: Full roster for the year ---
        roster_lines = []
        for m in members:
            roster_lines.append(f"- {m['name']}, Role: {m['role']}, Department: {m['department']}")
        
        full_text = (
            f"FOSS-CIT Board Members for the {year_range} academic year.\n"
            f"The following people served on the FOSS-CIT board in {year_range}:\n\n"
            + "\n".join(roster_lines)
        )
        
        chunks.append({
            "id": f"board_json_{year_key}_full_{chunk_id}",
            "text": full_text,
            "source": "board_members_json",
            "year_range": year_range,
            "year_short": year_short,
            "chunk_size": len(full_text),
            "chunk_number": chunk_id
        })
        chunk_id += 1
        
        # --- Chunk 2+: Per-role chunks for better retrieval ---
        roles_dict = {}
        for m in members:
            role = m["role"]
            if role not in roles_dict:
                roles_dict[role] = []
            roles_dict[role].append(m)
        
        # Group small roles together, keep big ones separate
        current_group_lines = []
        current_group_roles = []
        
        for role, people in roles_dict.items():
            role_lines = [f"**{role}:**"]
            for p in people:
                role_lines.append(f"- {p['name']} ({p['department']})")
            
            current_group_lines.extend(role_lines)
            current_group_roles.append(role)
            
            # Flush when we have enough content
            if len(current_group_lines) >= 8:
                role_text = (
                    f"FOSS-CIT Board Members for {year_range} academic year — "
                    f"Roles: {', '.join(current_group_roles)}.\n\n"
                    + "\n".join(current_group_lines)
                )
                chunks.append({
                    "id": f"board_json_{year_key}_roles_{chunk_id}",
                    "text": role_text,
                    "source": "board_members_json",
                    "year_range": year_range,
                    "year_short": year_short,
                    "chunk_size": len(role_text),
                    "chunk_number": chunk_id
                })
                chunk_id += 1
                current_group_lines = []
                current_group_roles = []
        
        # Flush remaining
        if current_group_lines:
            role_text = (
                f"FOSS-CIT Board Members for {year_range} academic year — "
                f"Roles: {', '.join(current_group_roles)}.\n\n"
                + "\n".join(current_group_lines)
            )
            chunks.append({
                "id": f"board_json_{year_key}_roles_{chunk_id}",
                "text": role_text,
                "source": "board_members_json",
                "year_range": year_range,
                "year_short": year_short,
                "chunk_size": len(role_text),
                "chunk_number": chunk_id
            })
            chunk_id += 1
    
    print(f"✅ Created {len(chunks)} clean board member chunks from JSON")
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
        
        base_url = config["training_data"].get("website_url", "https://fosscit.netlify.app")
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
                metadata = {
                    "text": chunk['text'],
                    "source": chunk['source'],
                    "chunk_number": chunk.get('chunk_number', 0),
                    "chunk_size": chunk.get('chunk_size', 0)
                }
                
                # Add year_range and year_short for board member chunks
                if 'year_range' in chunk:
                    metadata['year_range'] = chunk['year_range']
                if 'year_short' in chunk:
                    metadata['year_short'] = chunk['year_short']
                
                vectors_to_upsert.append({
                    "id": chunk['id'],
                    "values": embedding,
                    "metadata": metadata
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
    
    # Load PDF files from config
    pdf_files = config["training_data"].get("pdf_files", [])
    
    for pdf_config in pdf_files:
        pdf_path = pdf_config["path"]
        source_name = pdf_config["source_name"]
        # Skip board member PDF - we use the clean JSON instead
        if "board" in source_name.lower():
            print(f"⏭️ Skipping {pdf_path} (using board_members.json instead)")
            continue
        if os.path.exists(pdf_path):
            text = extract_comprehensive_pdf_text(pdf_path)
            if text:
                chunks = create_smart_chunks(text, source_name)
                all_chunks.extend(chunks)
                print(f"📝 Created {len(chunks)} chunks from {source_name}")
        else:
            print(f"⚠️ File not found: {pdf_path}")
    
    # Add clean board member chunks from JSON
    board_chunks = create_board_member_chunks_from_json("board_members.json")
    all_chunks.extend(board_chunks)
    print(f"📋 Added {len(board_chunks)} clean board member chunks from JSON")
    
    # Add website data
    website_text = fetch_website_data()
    if website_text:
        website_chunks = create_smart_chunks(website_text, "website_data")
        all_chunks.extend(website_chunks)
        print(f"🌐 Created {len(website_chunks)} chunks from website")
    
    # Load manual knowledge from config
    manual_knowledge = config["training_data"].get("manual_knowledge", [])
    
    all_chunks.extend(manual_knowledge)
    print(f"📋 Added {len(manual_knowledge)} manual knowledge entries")
    
    # Save local knowledge base
    print("💾 Saving local knowledge base...")
    kb_file = config["file_paths"]["complete_knowledge_base"]
    with open(kb_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    
    print(f"📊 Total chunks created: {len(all_chunks)}")
    
    # Add to Pinecone
    success_count = add_chunks_to_pinecone(index, all_chunks)
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎉 KNOWLEDGE BASE CREATION COMPLETE!")
    print("=" * 60)
    print(f"📁 Local file: {kb_file} ({len(all_chunks)} chunks)")
    print(f"☁️ Pinecone vectors: {success_count} uploaded successfully")
    print(f"🔍 Embedding model: {embedding_model_name} (local, no API costs!)")
    print(f"📡 Vector database: Pinecone ({PINECONE_INDEX_NAME})")
    print("✅ Ready for semantic search!")

if __name__ == "__main__":
    main()