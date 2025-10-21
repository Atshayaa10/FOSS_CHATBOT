# FOSS-CIT AI Chatbot

An intelligent chatbot for the Free and Open Source Software Community at Coimbatore Institute of Technology, powered by OpenRouter, Sentence Transformers, and Pinecone vector database.

## 🎯 Features

- **Semantic Search**: Uses local embeddings to understand meaning, not just keywords
- **PDF Knowledge Base**: Extracts and indexes content from FOSS-CIT documents
- **OpenRouter Integration**: Intelligent chat responses using GPT-3.5-turbo
- **Pinecone Vector Database**: Fast, accurate semantic search capabilities
- **Local Embeddings**: No additional API costs for embeddings using Sentence Transformers
- **Comprehensive Knowledge**: 77+ chunks from PDFs, website data, and manual entries

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Virtual environment (venv)
- OpenRouter API key
- Pinecone API key

### Installation

1. **Clone or download the project**

2. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=sk-or-v1-your-openrouter-key-here
   PINECONE_API_KEY=your-pinecone-key-here
   OPENAI_CHAT_MODEL=gpt-3.5-turbo
   ```

3. **Install dependencies**
   ```powershell
   .\venv\Scripts\pip.exe install -r req.txt
   ```

4. **Run the bot**
   ```powershell
   .\venv\Scripts\python.exe openrouter_pinecone_bot.py
   ```

## 📁 Project Structure

```
chatbotnew/
├── openrouter_pinecone_bot.py      # Main bot server
├── openrouter_pinecone_train.py    # Knowledge base creation script
├── chat.html                        # Chat interface
├── complete_knowledge_base.json    # Local knowledge base backup
├── req.txt                          # Python dependencies
├── .env                             # Environment variables (create this)
├── start_bot.ps1                    # PowerShell startup script
└── data/                            # PDF documents
    ├── About FOSS-CIT.pdf
    └── FOSS-CIT SOP.pdf
```

## 🌐 Usage

### Starting the Bot

**Method 1: Direct Python**
```powershell
cd "C:\Users\Aradhana S\OneDrive\Documents\chatbotnew"
.\venv\Scripts\python.exe openrouter_pinecone_bot.py
```

**Method 2: PowerShell Script** (if script execution is enabled)
```powershell
.\start_bot.ps1
```

### Accessing the Chat Interface

Once the bot is running, open your browser and navigate to:

- **Main Interface**: http://127.0.0.1:5000
- **Chat Interface**: http://127.0.0.1:5000/chat.html
- **Health Check**: http://127.0.0.1:5000/health

### Sample Questions

Try asking the bot:

- "Who founded FOSS-CIT?"
- "What is FOSS-CIT about?"
- "How can I contribute to open source?"
- "What are the FOSS-CIT procedures?"
- "Tell me about programming careers"
- "How to start learning programming?"

## 🛠️ Technical Stack

### Backend
- **Flask**: Web server framework
- **OpenRouter**: GPT-3.5-turbo for chat responses
- **Sentence Transformers**: Local embeddings (all-MiniLM-L6-v2)
- **Pinecone**: Vector database for semantic search
- **PyPDF2**: PDF text extraction

### Frontend
- **HTML/CSS/JavaScript**: Chat interface
- **Fetch API**: Backend communication

### Key Dependencies
```
flask==3.0.7
flask-cors==3.0.10
python-dotenv==1.0.0
openai==1.35.0
pinecone-client==5.0.1
PyPDF2==3.0.1
requests==2.31.0
sentence-transformers==3.0.1
beautifulsoup4==4.12.3
```

## 🔧 How It Works

### 1. Knowledge Base Creation
- Extracts all text from PDF documents
- Chunks content into 500-word segments with overlap
- Generates embeddings using local Sentence Transformers model
- Uploads vectors to Pinecone for semantic search
- Creates local backup in `complete_knowledge_base.json`

### 2. Query Processing
1. User sends a question via chat interface
2. Question is embedded using local model (no API cost)
3. Pinecone searches for most relevant content chunks
4. Top 3 relevant chunks are used as context
5. OpenRouter generates intelligent response using context
6. Response is returned to user

### 3. Fallback System
- Primary: Pinecone semantic search
- Fallback: Local keyword-based search if Pinecone unavailable
- Always maintains local knowledge base for reliability

## 📊 Cost Efficiency

### Embeddings: FREE
- Uses local Sentence Transformers model
- No API calls for embeddings
- Fast inference on local machine

### Chat Responses: OpenRouter
- Only charges for chat completions
- Approximately $0.002 per 1K tokens
- Very cost-effective for typical usage

## 🔍 API Endpoints

### `GET /`
Home page with system information

### `GET /chat.html`
Chat interface

### `GET /health`
Health check endpoint
```json
{
  "status": "healthy",
  "openrouter": "connected",
  "pinecone": "connected",
  "knowledge_base": "77 chunks loaded",
  "embedding_model": "sentence-transformers (local)"
}
```

### `POST /chat`
Main chat endpoint

**Request:**
```json
{
  "message": "Your question here"
}
```

**Response:**
```json
{
  "response": "AI generated response",
  "sources_used": 3,
  "search_method": "pinecone"
}
```

## 🐛 Troubleshooting

### Bot not starting?
- Check if port 5000 is available
- Verify API keys in `.env` file
- Ensure all dependencies are installed

### Connection errors?
- Make sure the bot server is running
- Check that you're using `127.0.0.1:5000` not `localhost:5000`
- Verify CORS is enabled in the bot

### No responses from bot?
- Check OpenRouter API key is valid
- Verify internet connection
- Check terminal output for error messages

### Knowledge base not found?
Run the training script:
```powershell
.\venv\Scripts\python.exe openrouter_pinecone_train.py
```

## 📝 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenRouter API key | `sk-or-v1-...` |
| `PINECONE_API_KEY` | Pinecone API key | `pcsk_...` |
| `OPENAI_CHAT_MODEL` | Chat model to use | `gpt-3.5-turbo` |

### Customization

- **Embedding Model**: Change in `openrouter_pinecone_train.py` and `openrouter_pinecone_bot.py`
- **Chunk Size**: Modify `chunk_size` parameter in `create_smart_chunks()`
- **Search Results**: Adjust `top_k` parameter in search functions
- **Response Length**: Change `max_tokens` in chat completions

## 📚 Adding More Documents

1. Place PDF files in the `data/` folder
2. Update `pdf_files` list in `openrouter_pinecone_train.py`
3. Run the training script to rebuild the knowledge base

## 🤝 Contributing

This is a project for FOSS-CIT. To contribute:
1. Add more PDF documents to the knowledge base
2. Improve the chat interface
3. Enhance the search algorithms
4. Add more manual knowledge entries

## 📄 License

Free and Open Source Software - FOSS-CIT Community Project

## 👥 Credits

**FOSS-CIT Founded by:**
- Dhileepan Thangamanimaran
- Sai Adarsh
- Sibi Bose

**Technologies:**
- OpenRouter (OpenAI API)
- Pinecone Vector Database
- Sentence Transformers
- Flask Web Framework

---

**For questions or support, contact the FOSS-CIT community at Coimbatore Institute of Technology.**