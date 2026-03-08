# openrouter_pinecone_bot.py - Enhanced Bot with OpenRouter + Sentence Transformers
import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import time

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
        "api_config": {"chat_model": "gpt-3.5-turbo", "pinecone_index_name": "foss-cit-knowledge"},
        "file_paths": {"complete_knowledge_base": "complete_knowledge_base.json"},
        "hardcoded_responses": {},
        "search_config": {"top_k": 3, "similarity_threshold": 0.6},
        "response_config": {"max_tokens_comprehensive": 500, "temperature": 0.7},
        "ai_prompts": {"system_prompt_comprehensive": "", "default_local_response": ""}
    }

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = config["api_config"].get("pinecone_index_name", "foss-cit-knowledge")
CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", config["api_config"]["chat_model"])

print("🚀 FOSS-CIT Enhanced Bot with OpenRouter + Local Embeddings")
print("=" * 60)

# Initialize OpenAI/OpenRouter client for chat
if OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-or-"):
    print("🤖 Initializing OpenRouter for chat responses...")
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )
else:
    print("🤖 Initializing OpenAI for chat responses...")
    client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize local embedding model
print("📦 Loading local embedding model...")
embedding_model_name = config["api_config"].get("embedding_model", "all-MiniLM-L6-v2")
embedding_model = SentenceTransformer(embedding_model_name)
print(f"✅ Local embedding model loaded: {embedding_model_name}")

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

# Rate limiting setup - 15 requests per minute
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["15 per minute"],
    storage_uri="memory://"
)
print("🛡️ Rate limiting enabled: 15 requests per minute per IP")

# Conversation history storage - keeps last N exchanges per user
conversation_history = {}
MAX_HISTORY_LENGTH = config.get("conversation_config", {}).get("max_history_length", 15)
print(f"💭 Conversation memory enabled: Last {MAX_HISTORY_LENGTH} exchanges per user")

# Load local knowledge base as fallback
knowledge_base = []
try:
    kb_file = config["file_paths"]["complete_knowledge_base"]
    with open(kb_file, 'r', encoding='utf-8') as f:
        knowledge_base = json.load(f)
        print(f"📚 Loaded comprehensive knowledge base with {len(knowledge_base)} chunks")
except FileNotFoundError:
    print("⚠️ No local knowledge base found. Run training script first.")
except Exception as e:
    print(f"❌ Error loading knowledge base: {e}")

# Load structured board members data
board_members_data = {}
try:
    with open('board_members.json', 'r', encoding='utf-8') as f:
        board_members_data = json.load(f)
    print(f"📋 Loaded board members for {len(board_members_data)} academic years")
except FileNotFoundError:
    print("⚠️ board_members.json not found.")
except Exception as e:
    print(f"❌ Error loading board members: {e}")

def get_board_response(user_message):
    """Handle board member queries using structured JSON data. Returns None if not a board query."""
    import re
    query_lower = user_message.lower()
    
    # Check if this is a board member query
    board_keywords = ['board', 'member', 'secretary', 'president', 'treasurer',
                      'coordinator', 'joint secretary', 'innovation head',
                      'editing', 'technical team', 'event manager', 'social media',
                      'public relation', 'content writ', 'outreach', 'chairperson',
                      'head of']
    if not any(kw in query_lower for kw in board_keywords):
        return None
    
    # Determine which year the user is asking about
    year_mappings = {
        '2020': '2020-2021', '2021': '2020-2021',
        '2022': '2022-2023', '2023': '2023-2024',
        '2024': '2024-2025', '2025': '2025-2026', '2026': '2025-2026'
    }
    
    # Check for explicit year range first (e.g., "2024-2025")
    range_match = re.search(r'(20\d{2})\s*[-\u2013]\s*(20\d{2})', query_lower)
    if range_match:
        target_year = f"{range_match.group(1)}-{range_match.group(2)}"
    else:
        # Check for single year
        year_match = re.search(r'\b(202[0-6])\b', query_lower)
        if year_match:
            target_year = year_mappings.get(year_match.group(1), '2025-2026')
        else:
            # No year mentioned, use current year
            target_year = '2025-2026'
    
    print(f"📋 Board query detected, target year: {target_year}")
    
    # Get board data for the target year
    board_data = board_members_data.get(target_year)
    if not board_data:
        return f"I don't have board member data for the {target_year} academic year."
    
    members = board_data['members']
    
    # Check if user asks for a specific role
    role_keywords = {
        'secretary': ['secretary'],
        'joint secretary': ['joint secretary'],
        'treasurer': ['treasurer'],
        'innovation head': ['innovation head'],
        'event manager': ['event manager', 'head of event'],
        'technical team': ['technical team', 'head of technical'],
        'editing': ['editing team', 'head of editing'],
        'social media': ['social media'],
        'public relation': ['public relations'],
        'content writ': ['content writing'],
        'outreach': ['outreach coordinator'],
        'poster': ['poster designer'],
        'digital': ['digital media', 'digital assistant'],
        'contributor': ['contributor']
    }
    
    # Find which specific role is being asked about
    target_roles = None
    for keyword, roles in role_keywords.items():
        if keyword in query_lower:
            target_roles = roles
            break
    
    # Special: if "secretary" is asked but not "joint secretary", show only secretaries
    if target_roles and target_roles == ['secretary'] and 'joint' not in query_lower:
        filtered = [m for m in members if m['role'].lower() == 'secretary']
    elif target_roles:
        filtered = [m for m in members if any(r.lower() in m['role'].lower() for r in target_roles)]
    else:
        filtered = members  # Show all board members
    
    if not filtered:
        return f"I don't have data for that specific role in the {target_year} academic year."
    
    # Build clean response
    response = f"**Board Members for {target_year} academic year:**\n\n"
    
    if target_roles and len(filtered) <= 10:
        # Specific role query - show detailed format
        # Group by role
        roles_dict = {}
        for m in filtered:
            r = m['role']
            if r not in roles_dict:
                roles_dict[r] = []
            roles_dict[r].append(m)
        
        for role, people in roles_dict.items():
            response += f"**{role}:**\n"
            for p in people:
                response += f"- {p['name']} ({p['department']})\n"
            response += "\n"
    else:
        # All members - group by role
        roles_dict = {}
        for m in filtered:
            r = m['role']
            if r not in roles_dict:
                roles_dict[r] = []
            roles_dict[r].append(m)
        
        for role, people in roles_dict.items():
            response += f"**{role}:**\n"
            for p in people:
                response += f"- {p['name']} ({p['department']})\n"
            response += "\n"
    
    return response.strip()

def get_embedding(text):
    """Get embedding using local Sentence Transformer model."""
    try:
        # Use local model - no API calls needed!
        embedding = embedding_model.encode(text).tolist()
        return embedding
    except Exception as e:
        print(f"❌ Error getting embedding: {e}")
        return None
def expand_year_in_query(query):
    """Expand single years to ranges for better matching.
    
    Examples:
    - "in 2022" -> "in 2022-2023"
    - "2024 board" -> "2024-2025 board"
    - "2023 members" -> "2023-2024 members"
    """
    import re
    
    # Year range mapping (single year -> full range)
    year_mappings = {
        "2020": "2020-2021",
        "2021": "2020-2021",
        "2022": "2022-2023",
        "2023": "2023-2024",
        "2024": "2024-2025",
        "2025": "2025-2026",
        "2026": "2025-2026"
    }
    
    expanded_query = query
    
    # Pattern to match standalone years (not already in range format)
    # Looks for year NOT followed by dash/hyphen and another year
    pattern = r'\b(202[0-6])\b(?!\s*[-–]\s*\d{4})'
    
    def replace_year(match):
        year = match.group(1)
        return year_mappings.get(year, year)
    
    expanded_query = re.sub(pattern, replace_year, query)
    
    if expanded_query != query:
        print(f"📅 Expanded query: '{query}' -> '{expanded_query}'")
    
    return expanded_query

def _clean_response_formatting(response):
    """Clean up response formatting by replacing asterisks with proper bullets."""
    import re
    
    # Replace lines starting with asterisks (with optional spaces/indentation) with bullets
    # Pattern: optional spaces, then *, then space, then content
    response = re.sub(r'^(\s*)\*\s+', r'\1• ', response, flags=re.MULTILINE)
    
    return response

def _fuzzy_match(query_lower, keyword):
    """Check if a keyword fuzzy-matches in the query.
    Handles typos by checking if any query word shares a long common prefix with any keyword word."""
    query_words = query_lower.split()
    kw_words = keyword.split()
    
    for kw_word in kw_words:
        matched = False
        for qw in query_words:
            # Exact substring (only if query word is at least 4 chars to avoid "me" matching "member")
            if len(qw) >= 4 and (kw_word in qw or qw in kw_word):
                matched = True
                break
            # Exact word match (any length)
            if kw_word == qw:
                matched = True
                break
            # Common prefix of at least 4 chars (handles typos like secreatry/secretary, manages/manager)
            prefix_len = min(len(kw_word), len(qw))
            common = 0
            for i in range(prefix_len):
                if kw_word[i] == qw[i]:
                    common += 1
                else:
                    break
            if common >= 4:
                matched = True
                break
        if not matched:
            return False
    return True

def detect_board_query(query):
    """Detect if query is about board members and extract the target year."""
    import re
    query_lower = query.lower()
    
    # First, check if this is a recruitment/join query (NOT a board query)
    recruitment_keywords = ['join', 'become a member', 'become member', 'apply', 'recruit', 
                           'eligibility', 'how to join', 'how can i join', 'how do i join',
                           'how to become', 'how can i become', 'how do i become',
                           'application', 'form']
    is_recruitment = any(kw in query_lower for kw in recruitment_keywords)
    if is_recruitment:
        return False, None
    
    # Use fuzzy matching for board-related keywords
    board_stems = ['board', 'member', 'secretary', 'president', 'treasurer',
                   'coordinator', 'innovation', 'editing', 'technical',
                   'event manager', 'social media', 'public relation', 'content writ',
                   'outreach', 'chairperson', 'head of', 'manage', 'lead', 'run',
                   'who is the', 'who was the', 'who are the']
    is_board = any(_fuzzy_match(query_lower, kw) for kw in board_stems)
    if not is_board:
        return False, None
    
    year_mappings = {
        '2020': '2020-2021', '2021': '2020-2021',
        '2022': '2022-2023', '2023': '2023-2024',
        '2024': '2024-2025', '2025': '2025-2026', '2026': '2025-2026'
    }
    
    range_match = re.search(r'(20\d{2})\s*[-\u2013]\s*(20\d{2})', query_lower)
    if range_match:
        target_year = f"{range_match.group(1)}-{range_match.group(2)}"
    else:
        year_match = re.search(r'\b(202[0-6])\b', query_lower)
        if year_match:
            target_year = year_mappings.get(year_match.group(1), '2025-2026')
        else:
            target_year = '2025-2026'
    
    return True, target_year

def get_board_context_from_json(target_year, user_message):
    """Build rich context string from board_members.json for the AI.
    Returns (context_string, has_specific_role) tuple."""
    import re
    if not board_members_data:
        return "", False
    
    board_data = board_members_data.get(target_year)
    if not board_data:
        return "", False
    
    members = board_data['members']
    query_lower = user_message.lower()
    
    # Check if asking about a specific role
    # Order matters: check longer/more-specific keywords first
    # Uses fuzzy matching to handle typos (e.g. "secreatry", "manages", "techincal")
    role_keywords = [
        ('joint secretary', 'joint secretary'),
        ('head of technical', 'head of technical team'),
        ('head of editing', 'head of editing team'),
        ('head of event', 'head of event management'),
        ('technical team', 'technical team'),
        ('editing team', 'editing team'),
        ('editing', 'editing team'),
        ('innovation', 'innovation head'),
        ('event manag', 'event manager'),
        ('social media', 'social media'),
        ('public relation', 'public relations'),
        ('content writ', 'content writing'),
        ('outreach', 'outreach coordinator'),
        ('poster', 'poster designer'),
        ('digital', 'digital'),
        ('contributor', 'contributor'),
        ('secretary', 'secretary'),
        ('treasurer', 'treasurer'),
    ]
    
    target_role = None
    for keyword, role_label in role_keywords:
        if _fuzzy_match(query_lower, keyword):
            target_role = role_label
            break
    
    # Build structured context
    roles_dict = {}
    for m in members:
        r = m['role']
        if r not in roles_dict:
            roles_dict[r] = []
        roles_dict[r].append(m)
    
    has_specific_role = False
    if target_role:
        # Filter to matching roles
        if target_role == 'secretary' and 'joint' not in query_lower:
            filtered_roles = {k: v for k, v in roles_dict.items() if k.lower() == 'secretary'}
        else:
            filtered_roles = {k: v for k, v in roles_dict.items()
                             if target_role.lower() in k.lower()}
        if filtered_roles:
            roles_dict = filtered_roles
            has_specific_role = True
    
    lines = [f"FOSS-CIT Board Members for the {target_year} academic year:"]
    for role, people in roles_dict.items():
        lines.append(f"\n{role}:")
        for p in people:
            lines.append(f"- {p['name']} (Department: {p['department']})")
    
    return "\n".join(lines), has_specific_role

def search_pinecone(query, top_k=None, metadata_filter=None):
    """Search Pinecone for relevant chunks, with optional metadata filtering."""
    if not PINECONE_AVAILABLE or not pinecone_index:
        return []
    
    if top_k is None:
        top_k = config["search_config"]["top_k"]
    
    try:
        query_embedding = get_embedding(query)
        if not query_embedding:
            return []
        
        query_params = {
            "vector": query_embedding,
            "top_k": top_k,
            "include_metadata": True
        }
        if metadata_filter:
            query_params["filter"] = metadata_filter
        
        results = pinecone_index.query(**query_params)
        
        similarity_threshold = config["search_config"]["similarity_threshold"]
        relevant_chunks = []
        for match in results.matches:
            if match.score > similarity_threshold:
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

def search_local_knowledge(query, top_k=None):
    """Search local knowledge base for relevant information."""
    if not knowledge_base:
        return []
    
    if top_k is None:
        top_k = config["search_config"]["top_k"]
    
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

# Load hardcoded responses from config
HARDCODED_RESPONSES = config.get("hardcoded_responses", {})
ULTRA_BRIEF_RESPONSES = config.get("ultra_brief_responses", {})

def get_local_response(user_message, context_chunks, history=None):
    """Generate response locally using context, hardcoded responses, and conversation history."""
    import re
    query_lower = user_message.lower()
    
    # If this is a board query and we have board member context, use it directly
    is_board, _ = detect_board_query(user_message)
    if is_board and context_chunks and len(context_chunks) > 0:
        best_chunk = context_chunks[0]
        if best_chunk.get('source') == 'board_members_json':
            return best_chunk['text']
    
    # Check ultra brief responses (exact key matching)
    for key, response in ULTRA_BRIEF_RESPONSES.items():
        if key in query_lower:
            return response
    
    # Check hardcoded responses (keyword matching)
    for category, data in HARDCODED_RESPONSES.items():
        for keyword in data["keywords"]:
            if keyword in query_lower:
                return data["response"]
    
    # For vague follow-ups like "tell me more", use history to find last topic
    vague_patterns = ['tell me more', 'more about', 'elaborate', 'explain more', 'what else', 'go on', 'continue', 'and?', 'more info', 'details']
    is_followup = any(p in query_lower for p in vague_patterns)
    
    if is_followup and history and len(history) >= 2:
        # Re-search using the last user message as context
        last_user_msg = None
        for msg in reversed(history):
            if msg['role'] == 'user':
                last_user_msg = msg['content']
                break
        if last_user_msg:
            # Return the last assistant response as context
            last_bot_msg = None
            for msg in reversed(history):
                if msg['role'] == 'assistant':
                    last_bot_msg = msg['content']
                    break
            if last_bot_msg:
                return f"Continuing from our previous discussion: {last_bot_msg}"
    
    # Use context chunks if available (skip board chunks for non-board queries)
    if context_chunks and len(context_chunks) > 0:
        # Collect relevant text from multiple chunks
        relevant_texts = []
        for chunk in context_chunks[:3]:  # Use top 3 chunks
            if not is_board and chunk.get('source') == 'board_members_json':
                continue
            text = chunk['text']
            text = re.sub(r'---\s*Page\s*\d+\s*---', '', text).strip()
            if text:
                relevant_texts.append(text)
        
        if relevant_texts:
            # Try to create a structured response from the chunks
            combined = ' '.join(relevant_texts)
            
            # Format the response with better structure
            response = _format_local_response(user_message, combined)
            return response
    
    # Default response from config
    return config["ai_prompts"].get("default_local_response", "I'm the FOSS-CIT Assistant! Ask me about FOSS-CIT!")

def _format_local_response(query, text):
    """Format raw text into a structured, readable response."""
    import re
    
    # Clean up the text - remove page markers and extra whitespace
    text = re.sub(r'---\s*Page\s*\d+\s*---', '', text)
    text = re.sub(r'Page\s*\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    query_lower = query.lower()
    
    # Check if this is a recruitment/join query
    is_recruitment = any(keyword in query_lower for keyword in [
        'join', 'become', 'member', 'core member', 'recruit', 'eligibility', 
        'how to', 'apply', 'application'
    ])
    
    if is_recruitment and ('eligibility' in text.lower() or 'recruitment' in text.lower() or 'application' in text.lower()):
        response_parts = []
        response_parts.append("To become a member of FOSS-CIT:")
        
        # Eligibility
        if 'eligibility' in text.lower() or '2nd' in text or '3rd' in text:
            response_parts.append("\n**Eligibility:**")
            if '2nd' in text and '3rd' in text:
                response_parts.append("• Open to 2nd and 3rd year students")
            if 'coding' in text.lower() or 'basic' in text.lower():
                response_parts.append("• Basic coding knowledge required")
            if 'communication' in text.lower():
                response_parts.append("• Basic communication skills required")
        
        # Timeline
        if 'march' in text.lower() or 'april' in text.lower():
            response_parts.append("\n**Recruitment Timeline:**")
            response_parts.append("• March - April each year")
        
        # Process
        if 'application' in text.lower() or 'form' in text.lower() or 'website' in text.lower():
            response_parts.append("\n**Application Process:**")
            response_parts.append("1. Fill out the application form on the official FOSS-CIT website")
            if 'linkedin' in text.lower() or 'instagram' in text.lower():
                response_parts.append("2. Forms are promoted through social media (LinkedIn, Instagram, Discord, WhatsApp)")
            if 'interview' in text.lower():
                response_parts.append("3. Selected candidates will be called for an interview")
        
        if len(response_parts) > 1:
            return "\n".join(response_parts)
    
    # Check if this is about FOSS-CIT overview/history
    is_about_foss = any(keyword in query_lower for keyword in ['about', 'what is', 'tell me', 'foss club', 'foss-cit'])
    
    if is_about_foss and ('founded' in text.lower() or 'established' in text.lower()):
        # Extract key information
        response_parts = []
        
        # Overview
        if 'foss' in text.lower():
            response_parts.append("**FOSS-CIT** is the Free and Open Source Software Community at Coimbatore Institute of Technology.")
        
        # History - extract founding info
        founding_match = re.search(r'(founded|established|started)\s+in\s+(\d{4})', text, re.IGNORECASE)
        founders_match = re.search(r'by\s+([^.]+?)(?:\.|,|\s+students)', text, re.IGNORECASE)
        
        if founding_match:
            year = founding_match.group(2)
            response_parts.append(f"\n**History:**")
            founders_text = "Dhileepan Thangamanimaran, Sai Adarsh, and Sibi Bose" if founders_match else "student initiative"
            response_parts.append(f"• Founded in **{year}** by {founders_text}")
        
        # Members info
        members_match = re.search(r'(\d+)\+?\s*(?:active\s+)?members', text, re.IGNORECASE)
        if members_match:
            response_parts.append(f"• **{members_match.group(1)}+ active members**")
        
        # Growth info
        if 'team of 5' in text.lower() or 'started with' in text.lower():
            response_parts.append("• Started with just 5 members and grew into a successful community of 15+ core members")
        
        # Events info
        events_match = re.search(r'(\d+)\+?\s*(?:total\s+)?events', text, re.IGNORECASE)
        if events_match:
            response_parts.append(f"• Organized **{events_match.group(1)}+ events**")
        
        # Activities
        if 'bootcamp' in text.lower() or 'workshop' in text.lower() or 'hackathon' in text.lower():
            response_parts.append("\n**Activities:**")
            activities = []
            if 'bootcamp' in text.lower():
                activities.append("Bootcamps")
            if 'workshop' in text.lower():
                activities.append("Workshops")
            if 'hackathon' in text.lower():
                activities.append("Hackathons")
            if 'webinar' in text.lower():
                activities.append("Webinars")
            if 'contest' in text.lower():
                activities.append("Coding Contests")
            response_parts.append("• " + ", ".join(activities))
        
        if response_parts:
            return "\n".join(response_parts)
    
    # For other queries, clean up and return first 2-3 sentences
    # Remove partial words from PDF extraction issues
    text = re.sub(r'\ballery\b', 'gallery', text, flags=re.IGNORECASE)
    
    sentences = text.split('.')
    if len(sentences) > 3:
        text = '. '.join(sentences[:3]) + '.'
    
    # Add basic formatting for readability
    text = text.replace('●', '\n•')
    return text.strip()

def get_ai_response(user_message, context_chunks, history=None):
    """Generate AI response using OpenRouter with context and conversation history, with local fallback."""
    import time
    
    # Build context from relevant chunks
    context = ""
    if context_chunks:
        context = "Relevant information:\n"
        for i, chunk in enumerate(context_chunks[:5], 1):
            context += f"{i}. {chunk['text']}\n"
        context += "\n"
    
    # Use brief system prompt to save tokens (credit limit)
    system_prompt_template = config["ai_prompts"]["system_prompt_brief"]
    system_prompt = f"{system_prompt_template}\n\n{context}"
    
    response_cfg = config["response_config"]

    # Build messages array with history
    messages = [{"role": "system", "content": system_prompt}]
    
    # Only send last 2 exchanges (4 messages) to save tokens
    if history:
        recent_history = history[-4:]
        for msg in recent_history:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Add current user message
    messages.append({"role": "user", "content": user_message})

    # Retry up to 3 times for rate limit (429) errors
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=CHAT_MODEL,
                messages=messages,
                max_tokens=response_cfg["max_tokens_comprehensive"],
                temperature=response_cfg["temperature"]
            )
            result = response.choices[0].message.content if response.choices else None
            if result:
                return result
            print("⚠️ OpenRouter returned empty response")
            return get_local_response(user_message, context_chunks, history)
        except Exception as e:
            error_str = str(e)
            if '429' in error_str and attempt < 2:
                wait = 2 ** attempt + 1
                print(f"⚠️ Rate limited (attempt {attempt+1}/3), retrying in {wait}s...")
                time.sleep(wait)
                continue
            print(f"⚠️ OpenRouter API error: {e}")
            print("📝 Using local fallback response...")
            return get_local_response(user_message, context_chunks, history)
    # All retries exhausted
    return get_local_response(user_message, context_chunks, history)

@app.route('/')
def home():
    api_provider = "OpenRouter" if OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-or-") else "OpenAI"
    return f"""
    <h1>🤖 FOSS-CIT Enhanced AI Assistant</h1>
    <p><strong>Powered by:</strong></p>
    <ul>
        <li>🧠 {api_provider} for intelligent responses</li>
        <li>🔍 Local Sentence Transformers for embeddings</li>
        <li>☁️ Pinecone for semantic vector search</li>
        <li>📚 Comprehensive PDF knowledge base</li>
    </ul>
    <p><a href="/chat.html">Start Chatting →</a></p>
    <p><a href="/health">Check System Status</a></p>
    """

# Removed: chat.html route - using React frontend instead
# @app.route('/chat.html')
# def chat_page():
#     """Serve the chat HTML page."""
#     return send_from_directory('.', 'chat.html')

@app.route('/health')
def health():
    """Health check endpoint."""
    api_provider = "openrouter" if OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-or-") else "openai"
    status = {
        "status": "healthy",
        "ai_provider": api_provider,
        "api_key_status": "connected" if OPENAI_API_KEY else "missing_key",
        "pinecone": "connected" if PINECONE_AVAILABLE else "disconnected",
        "knowledge_base": f"{len(knowledge_base)} chunks loaded",
        "embedding_model": f"{embedding_model_name} (local)",
        "hardcoded_responses": len(HARDCODED_RESPONSES),
        "conversation_memory": f"{len(conversation_history)} active sessions",
        "max_history_length": MAX_HISTORY_LENGTH
    }
    return jsonify(status)

@app.route('/chat', methods=['POST'])
@limiter.limit("15 per minute")
def chat():
    """Main chat endpoint with conversation memory."""
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
        
        # Get user identifier (IP address)
        user_id = get_remote_address()
        
        # Initialize or retrieve conversation history for this user
        if user_id not in conversation_history:
            conversation_history[user_id] = []
        
        user_history = conversation_history[user_id]
        
        print(f"💬 User ({user_id}): {user_message}")
        if user_history:
            print(f"📝 History: {len(user_history)} previous messages")
        
        # Expand years in query for better matching
        search_query = expand_year_in_query(user_message)
        
        # Check if this is a board member query
        is_board, target_year = detect_board_query(user_message)
        
        relevant_chunks = []
        board_context = ""
        
        if is_board and target_year:
            # For board queries: get filtered JSON context
            print(f"📋 Board query detected, target year: {target_year}")
            board_context, has_specific_role = get_board_context_from_json(target_year, user_message)
            
            if has_specific_role and board_context:
                # Specific role asked (e.g. "secretary") — use ONLY the filtered JSON,
                # don't add Pinecone full-roster chunks that would confuse the AI
                print(f"🎯 Specific role query — using filtered JSON context only")
            else:
                # General board query (e.g. "who are the board members") — also search Pinecone
                if PINECONE_AVAILABLE:
                    metadata_filter = {"source": "board_members_json"}
                    relevant_chunks = search_pinecone(search_query, top_k=8, metadata_filter=metadata_filter)
                    if len(relevant_chunks) < 2:
                        relevant_chunks.extend(search_pinecone(search_query))
                if len(relevant_chunks) < 2:
                    local_chunks = search_local_knowledge(search_query)
                    relevant_chunks.extend(local_chunks)
        else:
            # Non-board query: standard RAG
            if PINECONE_AVAILABLE:
                relevant_chunks = search_pinecone(search_query)
            if len(relevant_chunks) < 2:
                local_chunks = search_local_knowledge(search_query)
                relevant_chunks.extend(local_chunks)
        
        # Deduplicate
        seen_texts = set()
        unique_chunks = []
        for chunk in relevant_chunks:
            if chunk['text'] not in seen_texts:
                unique_chunks.append(chunk)
                seen_texts.add(chunk['text'])
                if len(unique_chunks) >= 5:
                    break
        
        # If we have board context from JSON, prepend it as the top chunk
        if board_context:
            unique_chunks.insert(0, {
                'text': board_context,
                'source': 'board_members_json',
                'score': 1.0
            })
        
        response = get_ai_response(user_message, unique_chunks, user_history)
        sources_used = len(unique_chunks)
        
        # Clean up formatting: replace asterisks with bullets
        response = _clean_response_formatting(response)
        
        print(f"🤖 Assistant: {response[:100]}...")
        
        # Update conversation history
        user_history.append({"role": "user", "content": user_message})
        user_history.append({"role": "assistant", "content": response})
        
        # Keep only last MAX_HISTORY_LENGTH exchanges (each exchange = user + assistant message)
        if len(user_history) > MAX_HISTORY_LENGTH * 2:
            conversation_history[user_id] = user_history[-(MAX_HISTORY_LENGTH * 2):]
        
        return jsonify({
            'response': response,
            'sources_used': sources_used,
            'search_method': 'pinecone' if PINECONE_AVAILABLE else 'local',
            'history_length': len(conversation_history[user_id]) // 2
        })
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/clear_history', methods=['POST'])
def clear_history():
    """Clear conversation history for the current user."""
    try:
        user_id = get_remote_address()
        if user_id in conversation_history:
            del conversation_history[user_id]
            print(f"🗑️ Cleared conversation history for {user_id}")
            return jsonify({
                'success': True,
                'message': 'Conversation history cleared'
            })
        else:
            return jsonify({
                'success': True,
                'message': 'No history to clear'
            })
    except Exception as e:
        print(f"❌ Error clearing history: {e}")
        return jsonify({'error': 'Failed to clear history'}), 500

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🌐 Starting FOSS-CIT Enhanced Bot Server...")
    print("=" * 60)
    flask_cfg = config.get("flask_config", {"host": "127.0.0.1", "port": 5000, "debug": True})
    print(f"🔗 API Endpoint: http://{flask_cfg['host']}:{flask_cfg['port']}/chat")
    print(f"💬 React Frontend: http://localhost:3000 (run separately)")
    print(f"📊 Health check: http://{flask_cfg['host']}:{flask_cfg['port']}/health")
    print("=" * 60)
    
    app.run(debug=flask_cfg.get("debug", True), host=flask_cfg["host"], port=flask_cfg["port"])