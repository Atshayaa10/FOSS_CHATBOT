# 🤖 Chatbot Widget Integration Guide

## 📦 Installation

### 1. Copy Component Files
Copy the following files to your React project:
```
src/
  components/
    ChatbotWidget.jsx
    ChatbotWidget.css
```

### 2. Import in Your App

#### Option A: Add to Main App Component (Recommended)
```jsx
// src/App.jsx
import React from 'react';
import ChatbotWidget from './components/ChatbotWidget';

function App() {
  return (
    <div className="App">
      {/* Your existing app content */}
      <YourRoutes />
      <YourComponents />
      
      {/* Add chatbot widget at the end */}
      <ChatbotWidget apiUrl="http://127.0.0.1:5000/chat" />
    </div>
  );
}

export default App;
```

#### Option B: Add to Root Layout
```jsx
// src/main.jsx or src/index.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import ChatbotWidget from './components/ChatbotWidget';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
    <ChatbotWidget apiUrl="http://127.0.0.1:5000/chat" />
  </React.StrictMode>
);
```

### 3. Configure API URL

Update the `apiUrl` prop based on your environment:

```jsx
// Development (default)
<ChatbotWidget apiUrl="http://127.0.0.1:5000/chat" />

// Production (update to your deployed backend)
<ChatbotWidget apiUrl="https://your-api-domain.com/chat" />

// Using environment variables (recommended)
<ChatbotWidget apiUrl={import.meta.env.VITE_CHATBOT_API_URL} />
```

Then create a `.env` file:
```env
# .env.development
VITE_CHATBOT_API_URL=http://127.0.0.1:5000/chat

# .env.production
VITE_CHATBOT_API_URL=https://your-api-domain.com/chat
```

---

## 🎨 Styling Options

### Option 1: Using Tailwind CSS (Minimal Changes Required)
The component works perfectly with Tailwind but uses CSS modules for component-specific styling.

**No changes needed!** Just ensure `ChatbotWidget.css` is imported.

### Option 2: Custom Styling
To customize colors and design:

```css
/* ChatbotWidget.css */

/* Change gradient colors */
.chatbot-toggle-btn,
.chatbot-header,
.message-avatar,
.chatbot-send-btn {
  background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
}

/* Change position */
.chatbot-widget {
  bottom: 20px;  /* Change bottom spacing */
  right: 20px;   /* Change to 'left' for left positioning */
}
```

---

## 🔧 API Integration

### Expected Request Format
```json
POST /chat
Content-Type: application/json

{
  "message": "user's message text"
}
```

### Expected Response Format
```json
{
  "response": "bot's reply text"
}
```
OR
```json
{
  "reply": "bot's reply text"
}
```

### CORS Configuration
Make sure your Flask backend allows requests from your React app:

```python
# In your Flask app (bot.py or openrouter_pinecone_bot.py)
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "https://your-netlify-domain.netlify.app"])
```

---

## 🚀 Deployment on Netlify

### 1. Update Environment Variables
In Netlify dashboard:
- Go to **Site settings** → **Environment variables**
- Add: `VITE_CHATBOT_API_URL` = `https://your-backend-api.com/chat`

### 2. Build Settings
Ensure `netlify.toml` or build settings are correct:
```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### 3. Deploy Backend API
Your Flask backend needs to be deployed separately:
- **Heroku**
- **Railway**
- **Render**
- **AWS/GCP/Azure**

Then update the `apiUrl` prop to point to your deployed backend.

---

## ✨ Features Included

✅ **Floating chat icon** - Fixed bottom-right position  
✅ **Toggle open/close** - Smooth slide animations  
✅ **Responsive design** - Works on mobile and desktop  
✅ **Auto-scroll** - Automatically scrolls to latest message  
✅ **Loading indicator** - Shows typing animation while waiting  
✅ **Error handling** - Graceful fallback on API errors  
✅ **Message history** - Keeps conversation in UI  
✅ **Enter to send** - Press Enter key to send message  
✅ **Clear history** - Button to reset conversation  
✅ **Timestamps** - Shows time for each message  
✅ **Modern UI** - Clean gradient design with animations  

---

## 📱 Component Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `apiUrl` | string | `http://127.0.0.1:5000/chat` | Backend API endpoint URL |

---

## 🎯 Usage Examples

### Basic Usage
```jsx
import ChatbotWidget from './components/ChatbotWidget';

<ChatbotWidget />
```

### With Custom API
```jsx
<ChatbotWidget apiUrl="https://api.example.com/chat" />
```

### With Environment Variable
```jsx
<ChatbotWidget apiUrl={import.meta.env.VITE_CHATBOT_API_URL || 'http://localhost:5000/chat'} />
```

---

## 🛠️ Troubleshooting

### Issue: Widget doesn't appear
**Solution:** Ensure the component is rendered and CSS is imported properly.

### Issue: CORS error
**Solution:** Configure Flask CORS to allow your React app's domain:
```python
CORS(app, origins=["http://localhost:5173", "https://your-site.netlify.app"])
```

### Issue: Messages not sending
**Solution:** Check:
1. Backend is running
2. API URL is correct
3. Backend returns proper JSON format: `{ "response": "text" }`

### Issue: Styling conflicts
**Solution:** The component uses scoped class names starting with `.chatbot-*` to avoid conflicts.

---

## 🎨 Customization Examples

### Change Position to Bottom-Left
```css
.chatbot-widget {
  left: 20px;
  right: auto;
}
```

### Change Color Scheme (Green)
```css
.chatbot-toggle-btn,
.chatbot-header,
.message-avatar,
.chatbot-send-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}
```

### Make Widget Larger
```css
.chatbot-window {
  width: 450px;
  height: 650px;
}
```

---

## 📝 Notes

- The widget uses React hooks (useState, useEffect, useRef)
- No external UI libraries required
- Compatible with React Router (doesn't interfere with routing)
- Z-index set to 9999 to float above other content
- Mobile responsive with media queries
- Includes fade/slide animations for smooth UX

---

## 🚦 Production Checklist

Before deploying to Netlify:

- [ ] Update `apiUrl` to production backend URL
- [ ] Configure CORS on backend for your Netlify domain
- [ ] Test on mobile devices
- [ ] Verify loading states work properly
- [ ] Test error handling (disconnect backend temporarily)
- [ ] Check Z-index doesn't conflict with existing modals
- [ ] Verify animations work smoothly
- [ ] Test enter key functionality
- [ ] Ensure auto-scroll works with long conversations

---

## 🎉 You're All Set!

Your floating chatbot widget is now ready to use. It will:
- Float at the bottom-right corner
- Open/close on click
- Connect to your existing Flask chatbot backend
- Work seamlessly with your React + Vite + Netlify stack

**Need help?** Check the component code comments or modify styles in `ChatbotWidget.css`.
