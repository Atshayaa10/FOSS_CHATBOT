"""
Flask Backend CORS Configuration for React Chatbot Widget
Add this to your Flask chatbot file (openrouter_pinecone_bot.py or bot.py)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# ============================================
# CORS Configuration Options
# ============================================

# Option 1: Allow all origins (NOT recommended for production)
# CORS(app)

# Option 2: Specific origins (RECOMMENDED)
CORS(app, origins=[
    "http://localhost:5173",              # Vite dev server
    "http://localhost:3000",              # Alternative React dev port
    "http://127.0.0.1:5173",              # Alternative localhost
    "https://your-site.netlify.app",      # Your Netlify production URL
    "https://your-custom-domain.com"      # Your custom domain
])

# Option 3: Advanced CORS with credentials
CORS(app, 
     origins=["http://localhost:5173", "https://your-site.netlify.app"],
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "OPTIONS"])

# ============================================
# Chat Endpoint Example
# ============================================

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Your chatbot logic here
        bot_response = get_bot_response(user_message)  # Your function
        
        # Return response in expected format
        return jsonify({
            'response': bot_response,    # Primary format
            'reply': bot_response,       # Alternative format (component supports both)
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'response': 'Sorry, I encountered an error. Please try again.',
            'success': False
        }), 500

# ============================================
# Health Check Endpoint (optional but recommended)
# ============================================

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'online',
        'service': 'FOSS-CIT Chatbot',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)


# ============================================
# Netlify Deployment CORS Configuration
# ============================================

"""
When deploying to production:

1. Update origins list with your actual Netlify URL:
   CORS(app, origins=["https://your-actual-site.netlify.app"])

2. If using custom domain on Netlify:
   CORS(app, origins=["https://yourdomain.com"])

3. For multiple environments:
   import os
   
   ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173').split(',')
   CORS(app, origins=ALLOWED_ORIGINS)
   
   Then set environment variable on your hosting platform:
   ALLOWED_ORIGINS=http://localhost:5173,https://your-site.netlify.app
"""

# ============================================
# Common CORS Issues & Solutions
# ============================================

"""
Issue 1: "CORS policy: No 'Access-Control-Allow-Origin' header"
Solution: Ensure flask-cors is installed and CORS(app) is called

Issue 2: "Preflight request didn't succeed"
Solution: Add OPTIONS method to route and return 204:
    @app.route('/chat', methods=['POST', 'OPTIONS'])
    if request.method == 'OPTIONS':
        return '', 204

Issue 3: Credentials not working
Solution: Add supports_credentials=True to CORS config

Issue 4: Custom headers blocked
Solution: Add allow_headers parameter with your headers

Issue 5: CORS works locally but not in production
Solution: Update origins list to include production domain
"""
