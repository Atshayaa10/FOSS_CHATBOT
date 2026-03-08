# 🎨 Advanced Customization Guide

## Color Themes

### 1. Modern Blue (Default)
```css
/* ChatbotWidget.css */
.chatbot-toggle-btn,
.chatbot-header,
.message-avatar,
.chatbot-send-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

### 2. Professional Green
```css
.chatbot-toggle-btn,
.chatbot-header,
.message-avatar,
.chatbot-send-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}
```

### 3. Vibrant Orange
```css
.chatbot-toggle-btn,
.chatbot-header,
.message-avatar,
.chatbot-send-btn {
  background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%);
}
```

### 4. Corporate Blue
```css
.chatbot-toggle-btn,
.chatbot-header,
.message-avatar,
.chatbot-send-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}
```

### 5. Dark Mode
```css
.chatbot-window {
  background: #1f2937;
}

.chatbot-header {
  background: linear-gradient(135deg, #374151 0%, #1f2937 100%);
}

.chatbot-messages {
  background: #111827;
}

.message-bubble {
  background: #374151;
  color: #f9fafb;
}

.chatbot-input {
  background: #374151;
  border-color: #4b5563;
  color: #f9fafb;
}
```

---

## 📍 Position Variants

### Bottom-Left
```css
.chatbot-widget {
  left: 20px;
  right: auto;
}

.chatbot-window {
  left: 20px;
  right: auto;
}
```

### Top-Right
```css
.chatbot-widget {
  top: 20px;
  bottom: auto;
}

.chatbot-window {
  top: 90px;
  bottom: auto;
}
```

### Center-Right (Full Height)
```css
.chatbot-window {
  top: 50%;
  transform: translateY(-50%);
  bottom: auto;
  height: 80vh;
}

.chatbot-window.open {
  transform: translateY(-50%) scale(1);
}
```

---

## 📐 Size Variants

### Compact
```css
.chatbot-window {
  width: 320px;
  height: 480px;
}

.chatbot-toggle-btn {
  width: 50px;
  height: 50px;
}
```

### Large
```css
.chatbot-window {
  width: 450px;
  height: 650px;
}

.chatbot-toggle-btn {
  width: 70px;
  height: 70px;
}
```

### Full Mobile
```css
@media (max-width: 768px) {
  .chatbot-window {
    width: 100vw;
    height: 100vh;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 0;
  }
}
```

---

## ✨ Animation Variants

### Bounce Entrance
```css
@keyframes bounceIn {
  0% {
    opacity: 0;
    transform: scale(0.3);
  }
  50% {
    transform: scale(1.05);
  }
  70% {
    transform: scale(0.9);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

.chatbot-window.open {
  animation: bounceIn 0.5s ease;
}
```

### Slide from Bottom
```css
@keyframes slideFromBottom {
  from {
    opacity: 0;
    transform: translateY(100%);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.chatbot-window.open {
  animation: slideFromBottom 0.4s ease;
}
```

### Fade Scale
```css
@keyframes fadeScale {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.chatbot-window.open {
  animation: fadeScale 0.3s ease;
}
```

---

## 🎯 Component Props Extension

To add more props, modify the component:

```jsx
// ChatbotWidget.jsx
const ChatbotWidget = ({ 
  apiUrl = 'http://127.0.0.1:5000/chat',
  position = 'bottom-right',          // NEW: 'bottom-right', 'bottom-left', etc.
  theme = 'blue',                     // NEW: 'blue', 'green', 'orange', 'dark'
  initialMessage = "Hi! How can I help?",  // NEW: Customize greeting
  botName = "FOSS-CIT Assistant",     // NEW: Customize bot name
  placeholder = "Type your message...", // NEW: Customize input placeholder
  enableSound = false,                 // NEW: Sound notifications
  maxHeight = 550,                    // NEW: Custom height
  maxWidth = 380,                     // NEW: Custom width
}) => {
  // Use these props in your component logic
  // ...
}
```

---

## 🔔 Add Sound Notifications

```jsx
// Add to ChatbotWidget.jsx
import { useEffect } from 'react';

const ChatbotWidget = (props) => {
  // ... existing code

  const playNotificationSound = () => {
    const audio = new Audio('/notification.mp3');
    audio.play().catch(err => console.log('Sound play failed:', err));
  };

  useEffect(() => {
    if (messages.length > 0 && messages[messages.length - 1].sender === 'bot') {
      playNotificationSound();
    }
  }, [messages]);

  // ... rest of component
}
```

---

## 💬 Add Quick Reply Buttons

```jsx
// Add after bot messages
const QuickReplies = ({ replies, onSelect }) => (
  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '8px' }}>
    {replies.map((reply, idx) => (
      <button
        key={idx}
        onClick={() => onSelect(reply)}
        style={{
          padding: '8px 12px',
          borderRadius: '16px',
          border: '1px solid #e5e7eb',
          background: 'white',
          cursor: 'pointer',
          fontSize: '13px'
        }}
      >
        {reply}
      </button>
    ))}
  </div>
);

// In your chat logic
const botMessageWithQuickReplies = {
  id: Date.now(),
  text: 'What would you like to know?',
  sender: 'bot',
  quickReplies: ['About Us', 'Events', 'Contact', 'Join FOSS']
};
```

---

## 📊 Add Typing Indicator Enhancement

```jsx
// Enhanced typing indicator with realistic timing
const [isTyping, setIsTyping] = useState(false);

const simulateTyping = (callback, duration = 1500) => {
  setIsTyping(true);
  setTimeout(() => {
    setIsTyping(false);
    callback();
  }, duration);
};

// Use before showing bot response
simulateTyping(() => {
  setMessages(prev => [...prev, botMessage]);
}, 1500);
```

---

## 🌐 Multi-language Support

```jsx
// Add language configuration
const translations = {
  en: {
    title: "FOSS-CIT Assistant",
    placeholder: "Type your message...",
    greeting: "Hi! How can I help you today?",
    status: "Online"
  },
  es: {
    title: "Asistente FOSS-CIT",
    placeholder: "Escribe tu mensaje...",
    greeting: "¡Hola! ¿Cómo puedo ayudarte hoy?",
    status: "En línea"
  }
};

const ChatbotWidget = ({ language = 'en', ...props }) => {
  const t = translations[language];
  
  // Use t.title, t.placeholder, etc. throughout component
}
```

---

## 🔐 Add Authentication (Optional)

```jsx
const ChatbotWidget = ({ apiUrl, userToken }) => {
  const sendMessage = async () => {
    // ... existing code
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userToken}` // Add auth header
      },
      body: JSON.stringify({ message: inputMessage }),
    });
    
    // ... rest of code
  };
}
```

---

## 📱 Add Mobile-Specific Features

```jsx
// Detect mobile
const [isMobile, setIsMobile] = useState(false);

useEffect(() => {
  const checkMobile = () => {
    setIsMobile(window.innerWidth <= 768);
  };
  
  checkMobile();
  window.addEventListener('resize', checkMobile);
  
  return () => window.removeEventListener('resize', checkMobile);
}, []);

// Use in render
{isMobile ? (
  <FullScreenChatWindow />
) : (
  <FloatingChatWindow />
)}
```

---

## 🎨 Icon Variants

### Custom Bot Icon (Replace SVG)
```jsx
// Replace the bot avatar SVG with custom icon
<div className="message-avatar">
  <img src="/bot-icon.png" alt="Bot" style={{ width: '24px', height: '24px' }} />
</div>
```

### Different Chat Icon
```jsx
// Replace toggle button SVG
<button className="chatbot-toggle-btn" onClick={toggleChat}>
  💬 {/* Or any emoji/icon */}
</button>
```

---

## 📈 Add Analytics

```jsx
const sendMessage = async () => {
  // ... existing code
  
  // Track with Google Analytics
  if (window.gtag) {
    window.gtag('event', 'chat_message_sent', {
      message_length: inputMessage.length,
      timestamp: new Date().toISOString()
    });
  }
  
  // Track with custom analytics
  fetch('/api/analytics', {
    method: 'POST',
    body: JSON.stringify({
      event: 'chat_message',
      message: inputMessage
    })
  });
};
```

---

## 🎪 Add Welcome Screen

```jsx
const [showWelcome, setShowWelcome] = useState(true);

{showWelcome && (
  <div className="welcome-screen">
    <h2>Welcome to FOSS-CIT!</h2>
    <p>I'm here to help with questions about our community.</p>
    <button onClick={() => setShowWelcome(false)}>Start Chat</button>
  </div>
)}
```

---

## ⚡ Performance Optimization

```jsx
import { memo, useMemo, useCallback } from 'react';

// Memoize message component
const Message = memo(({ message }) => (
  <div className={`chatbot-message ${message.sender}`}>
    {/* ... message content */}
  </div>
));

// Memoize expensive calculations
const sortedMessages = useMemo(() => {
  return messages.sort((a, b) => a.timestamp - b.timestamp);
}, [messages]);

// Memoize callbacks
const handleSend = useCallback(() => {
  sendMessage();
}, [inputMessage]);
```

---

## 🧪 Testing Tips

```jsx
// Add test mode prop
const ChatbotWidget = ({ testMode = false, ...props }) => {
  if (testMode) {
    // Mock API responses
    const mockResponse = { response: "This is a test response" };
    // Use mock instead of actual API
  }
}

// Usage
<ChatbotWidget testMode={true} />
```

---

## 🎁 Bonus: Add Emoji Picker

```jsx
import EmojiPicker from 'emoji-picker-react';

const [showEmojiPicker, setShowEmojiPicker] = useState(false);

const onEmojiClick = (emojiObject) => {
  setInputMessage(prev => prev + emojiObject.emoji);
};

// Add emoji button next to send button
<button onClick={() => setShowEmojiPicker(!showEmojiPicker)}>
  😊
</button>
```

---

These customizations allow you to fully tailor the chatbot widget to match your brand and requirements!
