# ultra_brief_bot.py - FOSS-CIT Chatbot with Ultra Brief Responses
import os
import re
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-3.5-turbo")

# Initialize OpenAI client
if OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-or-"):
    print("✅ Using OpenRouter for AI responses")
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )
else:
    print("✅ Using OpenAI directly")
    client = OpenAI(api_key=OPENAI_API_KEY)

# Flask app setup
app = Flask(__name__)
CORS(app)

# Load comprehensive knowledge base
knowledge_base = []
try:
    with open("comprehensive_knowledge_base.json", "r", encoding="utf-8") as f:
        knowledge_base = json.load(f)
    print(f"📚 Loaded comprehensive knowledge base with {len(knowledge_base)} chunks")
except FileNotFoundError:
    print("⚠️  comprehensive_knowledge_base.json not found. Run comprehensive_train.py first.")
except Exception as e:
    print(f"❌ Error loading brief knowledge base: {e}")

# -----------------------
# Ultra Brief Responses
# -----------------------
def get_ultra_brief_answer(question: str):
    """Get ultra brief answers - 1 sentence maximum."""
    question_lower = question.lower().strip()
    
    # Hard-coded ultra brief responses
    ultra_brief = {
        # Greetings
        'hello': "Hi! I help with FOSS-CIT info.",
        'hi': "Hello! What FOSS-CIT info do you need?",
        'hey': "Hey! Ask me about FOSS-CIT.",
        
        # About FOSS-CIT
        'what is foss-cit': "FOSS-CIT is a student organization at Coimbatore Institute of Technology that helps students learn open source technologies.",
        'what is foss cit': "FOSS-CIT is a student organization at Coimbatore Institute of Technology that helps students learn open source technologies.",
        'about foss-cit': "FOSS-CIT was founded by students at CIT to create a community for learning open source technologies.",
        'foss-cit mission': "To help students learn essential technical skills and work with open-source platforms.",
        'foss cit mission': "To help students learn essential technical skills and work with open-source platforms.",
        'founded foss-cit': "FOSS-CIT was founded in 2018 by Dhileepan Thangamanimaran, Sai Adarsh, and Sibi Bose.",
        'who founded foss-cit': "Dhileepan Thangamanimaran, Sai Adarsh, and Sibi Bose founded FOSS-CIT in 2018.",
        'history of foss-cit': "FOSS-CIT was established in 2018 by three CIT students: Dhileepan Thangamanimaran, Sai Adarsh, and Sibi Bose.",
        'founders of foss-cit': "The founders are Dhileepan Thangamanimaran, Sai Adarsh, and Sibi Bose.",
        'who initiated foss-cit': "Dhileepan Thangamanimaran, Sai Adarsh, and Sibi Bose initiated FOSS-CIT in 2018.",
        'who started foss-cit': "Dhileepan Thangamanimaran, Sai Adarsh, and Sibi Bose started FOSS-CIT.",
        
        # Activities
        'what activities': "Bootcamps, workshops, coding contests, hackathons, and career guidance.",
        'activities': "Bootcamps, workshops, coding contests, hackathons, and career guidance.",
        'events': "Bootcamps, workshops, contests, webinars, and meet-ups.",
        'programs': "Training bootcamps, workshops, coding contests, and interview prep.",
        'training': "We offer bootcamps, workshops, and hands-on coding sessions.",
        
        # Stats
        'how many members': "500+ active members.",
        'members': "500+ active members.",
        'achievements': "500+ members, training sessions, collaborations with Mozilla and Google.",
        
        # Contact
        'contact': "Email: fosscit@gmail.com, Location: CIT Coimbatore.",
        'location': "Department of Computing, CIT Coimbatore, Tamil Nadu.",
        'email': "fosscit@gmail.com",
        'address': "CIT Coimbatore, Avinashi Road, Peelamedu, Tamil Nadu 641014.",
        
        # Team
        'team': "Tharun Kailash K (Lead), Vignaraj D, Shriram R.",
        'who leads': "Tharun Kailash K is the team lead.",
        'leader': "Tharun Kailash K is the team lead.",
        
        # Tech questions
        'what can you do': "I provide quick FOSS-CIT info, events, and contact details.",
        'who are you': "FOSS-CIT AI assistant for quick info.",
        'help': "Ask about FOSS-CIT activities, team, or contact info.",
        
        # Programming
        'what is programming': "Writing code to create software and applications.",
        'how to start programming': "Start with Python, practice daily, build small projects.",
        'career advice': "Learn one language well, build projects, practice regularly.",
        'open source': "Free software that anyone can use, modify, and share.",
        'what is open source': "Free software that anyone can use, modify, and share.",
    }
    
    # Check for exact matches first
    for key, answer in ultra_brief.items():
        if key in question_lower:
            return answer
    
    # Search knowledge base for specific info
    context = search_comprehensive_knowledge(question, top_k=2)
    
    if context:
        # Extract key info from context
        if 'mission' in question_lower or 'objective' in question_lower:
            return "To assist students in learning essential technical skills and work with open-source platforms."
        elif 'activity' in question_lower or 'do' in question_lower:
            return "Bootcamps, workshops, coding contests, hackathons, and career guidance."
        elif 'member' in question_lower:
            return "500+ active members."
        elif 'contact' in question_lower or 'location' in question_lower:
            return "Email: fosscit@gmail.com, CIT Coimbatore."
        elif 'team' in question_lower:
            return "Tharun Kailash K (Lead), Vignaraj D, Shriram R."
        else:
            # Use AI for ultra brief response
            return generate_ai_brief_answer(question, context)
    
    # Fallback for general questions
    if any(word in question_lower for word in ['programming', 'code', 'software']):
        return "Programming is writing code to create software. Start with Python."
    elif any(word in question_lower for word in ['career', 'job', 'work']):
        return "Focus on learning one programming language well and building projects."
    else:
        return "I help with FOSS-CIT info. Ask about activities, team, or contact details."

def generate_ai_brief_answer(question: str, context: str):
    """Generate AI answer with comprehensive context but brief output."""
    try:
        # Use more context but still keep response brief
        context_summary = context[:300] + "..." if len(context) > 300 else context
        
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": "You are a FOSS-CIT expert. Give accurate, professional answers based on the context. Be direct and helpful. Answer in 1-2 sentences maximum."},
                {"role": "user", "content": f"Context about FOSS-CIT: {context_summary}\n\nQuestion: {question}\n\nProvide a direct, professional answer:"}
            ],
            temperature=0.2,
            max_tokens=80,
            top_p=0.9
        )
        
        answer = response.choices[0].message.content.strip()
        
        # Ensure brevity but allow 2 sentences
        sentences = answer.split('.')
        if len(sentences) > 2:
            answer = '. '.join(sentences[:2]) + '.'
        
        return answer
        
    except Exception as e:
        print(f"[Error] AI comprehensive answer failed: {e}")
        return "Sorry, I couldn't process that question right now."

def search_comprehensive_knowledge(query, top_k=2):
    """Enhanced search for comprehensive knowledge base with category scoring."""
    if not knowledge_base:
        return ""
    
    query_lower = query.lower().strip()
    query_words = set(re.findall(r'\w+', query_lower))
    
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    query_words = query_words - stop_words
    
    if not query_words:
        return ""
    
    scored_chunks = []
    
    for chunk in knowledge_base:
        chunk_text_lower = chunk['text'].lower()
        chunk_words = set(re.findall(r'\w+', chunk_text_lower))
        category = chunk.get('category', 'general')
        
        # Base scoring
        score = len(query_words.intersection(chunk_words))
        
        # Exact phrase match bonus
        if query_lower in chunk_text_lower:
            score += 15
        
        # Category-specific boosts
        if any(word in query_lower for word in ['founded', 'started', 'history', 'began', 'founder', 'initiated', 'establish']):
            if category in ['history', 'founders']:
                score += 15
        elif any(word in query_lower for word in ['mission', 'purpose', 'goal']):
            if category == 'mission':
                score += 10
        elif any(word in query_lower for word in ['team', 'members', 'people']):
            if category == 'team':
                score += 10
        elif any(word in query_lower for word in ['activities', 'events', 'programs']):
            if category == 'activities':
                score += 10
        elif any(word in query_lower for word in ['contact', 'email', 'location']):
            if category in ['contact', 'location']:
                score += 10
        
        # Length preference for detailed answers
        if len(chunk['text']) > 100:
            score += 2
        
        if score >= 1:
            scored_chunks.append((score, chunk['text']))
    
    # Sort by score and return top results
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    
    if scored_chunks:
        results = [chunk[1] for chunk in scored_chunks[:top_k]]
        return " ".join(results)
    
    return ""

# -----------------------
# Flask Routes
# -----------------------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        question = data.get("question", "").strip()
        
        if not question:
            return jsonify({
                "answer": "Please ask about FOSS-CIT!",
                "status": "error"
            }), 400

        print(f"❓ Question: {question}")
        
        # Get ultra brief answer
        answer = get_ultra_brief_answer(question)
        
        print(f"💬 Answer: {answer}")
        
        return jsonify({
            "answer": answer,
            "status": "success",
            "response_type": "professional"
        })

    except Exception as e:
        print(f"[Error] Chat failed: {e}")
        return jsonify({
            "answer": "Sorry, error occurred.",
            "status": "error"
        }), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "mode": "professional",
        "max_response": "direct_answers",
        "chunks": len(knowledge_base)
    })

@app.route("/chat.html", methods=["GET"])
def chat_page():
    try:
        with open("chat.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Chat interface not found.", 404

@app.route("/", methods=["GET"])
def home():
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>FOSS-CIT Ultra Brief Bot</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        h1 {{ color: #2c3e50; text-align: center; }}
        .status {{ background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .btn {{ display: inline-block; background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 FOSS-CIT Professional Bot</h1>
        
        <div class="status">
            <h3>✅ Status: Professional Mode</h3>
            <p><strong>Response Style:</strong> Direct, professional answers</p>
            <p><strong>Knowledge Base:</strong> {len(knowledge_base)} optimized chunks</p>
            <p><strong>Focus:</strong> Relevant, to-the-point responses</p>
        </div>

        <div style="text-align: center; margin-top: 30px;">
            <a href="/chat.html" class="btn">💬 Professional Chat</a>
            <a href="/health" class="btn">📊 Status</a>
        </div>
        
        <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px;">
            <h4>Try these:</h4>
            <ul>
                <li>"What is FOSS-CIT?" → 1 sentence</li>
                <li>"Activities?" → Brief list</li>
                <li>"Contact?" → Email and location</li>
                <li>"Team?" → Names only</li>
            </ul>
        </div>
    </div>
</body>
</html>"""

if __name__ == "__main__":
    print("⚡ Starting FOSS-CIT Professional Bot...")
    print("📝 Mode: Direct, professional answers")
    print("🌐 Access at: http://127.0.0.1:5000")
    app.run(debug=False, host='0.0.0.0', port=5000)