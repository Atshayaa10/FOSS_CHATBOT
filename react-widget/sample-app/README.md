# 🤖 FOSS-CIT Chatbot Widget Demo

A complete sample React application demonstrating the chatbot widget integration.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd sample-app
npm install
```

### 2. Make Sure Backend is Running
Ensure your Flask backend is running on port 5000:
```bash
cd ..
python openrouter_pinecone_bot.py
```

### 3. Start the React Development Server
```bash
npm run dev
```

The app will open automatically at **http://localhost:3000**

---

## 📁 Project Structure

```
sample-app/
├── index.html              # HTML entry point
├── package.json            # Dependencies
├── vite.config.js          # Vite configuration
├── src/
│   ├── main.jsx           # React entry point
│   ├── App.jsx            # Main application component
│   ├── App.css            # Application styles
│   ├── index.css          # Global styles
│   └── components/
│       ├── ChatbotWidget.jsx   # Chatbot widget component
│       └── ChatbotWidget.css   # Widget styles
```

---

## ✨ Features Demonstrated

✅ **Full Page Layout** - Complete website design with header, hero, features, footer  
✅ **Floating Chatbot** - Widget floats above all content  
✅ **Responsive Design** - Works on all screen sizes  
✅ **Easy Integration** - Single import, works anywhere  
✅ **Live Backend Connection** - Connects to Flask API at port 5000  

---

## 🎯 Using This Sample

### Option 1: Run As-Is (Standalone Demo)
```bash
npm install
npm run dev
```
Perfect for testing and development!

### Option 2: Integration into Existing Website

**Copy Just the Widget:**
```bash
# Copy these two files to your project
cp src/components/ChatbotWidget.jsx YOUR_PROJECT/src/components/
cp src/components/ChatbotWidget.css YOUR_PROJECT/src/components/
```

**Then import in your app:**
```jsx
import ChatbotWidget from './components/ChatbotWidget';

function YourApp() {
  return (
    <>
      {/* Your existing content */}
      <ChatbotWidget apiUrl="http://127.0.0.1:5000/chat" />
    </>
  );
}
```

**Copy Entire Sample (Modify the Design):**
```bash
# Copy the whole sample-app folder
# Then customize App.jsx and App.css to match your brand
```

---

## 🔧 Configuration

### Change Backend API URL
Edit `src/App.jsx`:
```jsx
<ChatbotWidget apiUrl="https://your-api-domain.com/chat" />
```

### Change Widget Colors
Edit `src/components/ChatbotWidget.css`:
```css
.chatbot-toggle-btn,
.chatbot-header {
  background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
}
```

### Change App Theme
Edit `src/App.css` and `src/index.css` to customize the website design.

---

## 📦 Production Build

Build for production:
```bash
npm run build
```

This creates a `dist/` folder ready for deployment to:
- Netlify
- Vercel
- GitHub Pages
- Any static hosting

---

## 🌐 Deployment

### Netlify Deployment

1. **Build the project:**
   ```bash
   npm run build
   ```

2. **Deploy to Netlify:**
   - Drag and drop the `dist/` folder to Netlify
   - Or connect your GitHub repo

3. **Set environment variable:**
   In Netlify dashboard, add:
   ```
   VITE_CHATBOT_API_URL=https://your-backend-api.com/chat
   ```

4. **Update App.jsx:**
   ```jsx
   <ChatbotWidget 
     apiUrl={import.meta.env.VITE_CHATBOT_API_URL || 'http://127.0.0.1:5000/chat'} 
   />
   ```

---

## 🎨 Customization Tips

### Make it Your Own:

1. **Change Colors**: Update gradients in both CSS files
2. **Modify Content**: Edit `App.jsx` to change text and sections
3. **Add Pages**: Use React Router for multiple pages
4. **Add Features**: Extend the widget with new functionality
5. **Brand It**: Replace the avatar icons and colors

---

## 🔍 Testing the Chatbot

Once running, click the purple chat icon in the bottom-right corner and try:
- "What is FOSS-CIT?"
- "Tell me about your events"
- "How can I join?"
- "Contact details"

---

## 🐛 Troubleshooting

**Widget doesn't appear:**
- Check browser console for errors
- Ensure CSS file is imported
- Verify component is rendered in App.jsx

**Can't send messages:**
- Ensure Flask backend is running on port 5000
- Check `apiUrl` in App.jsx is correct
- Open browser DevTools → Network tab to see API calls

**CORS errors:**
- Ensure Flask has CORS configured:
  ```python
  from flask_cors import CORS
  CORS(app, origins=["http://localhost:3000"])
  ```

**Styling issues:**
- Clear browser cache
- Check for CSS conflicts
- Ensure both CSS files are imported

---

## 💡 Integration Examples

### Example 1: Add to Existing Vite Project
```jsx
// In your existing App.jsx
import ChatbotWidget from './components/ChatbotWidget';

function App() {
  return (
    <div className="your-app">
      {/* Your existing content */}
      <ChatbotWidget apiUrl="http://127.0.0.1:5000/chat" />
    </div>
  );
}
```

### Example 2: Add to React Router App
```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ChatbotWidget from './components/ChatbotWidget';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
      </Routes>
      {/* Widget appears on all routes */}
      <ChatbotWidget apiUrl="http://127.0.0.1:5000/chat" />
    </BrowserRouter>
  );
}
```

### Example 3: Conditional Loading
```jsx
function App() {
  const [showChat, setShowChat] = useState(true);
  
  return (
    <>
      {/* Your content */}
      {showChat && <ChatbotWidget apiUrl="http://127.0.0.1:5000/chat" />}
    </>
  );
}
```

---

## 📚 Next Steps

1. ✅ Run this sample (`npm run dev`)
2. ✅ Test the chatbot functionality
3. ✅ Customize colors and content
4. ✅ Copy widget to your main project
5. ✅ Deploy to production

---

## 🎉 That's It!

You now have a fully functional React website with an integrated AI chatbot widget!

**Need help?** Check the main `INTEGRATION.md` in the parent `react-widget/` folder for detailed documentation.

Enjoy your new chatbot! 🚀
