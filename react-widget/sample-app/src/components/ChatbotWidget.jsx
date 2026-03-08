import React, { useState, useEffect, useRef } from 'react';
import './ChatbotWidget.css';

// Simple markdown renderer: bold, bullet lists, newlines
function renderMarkdown(text) {
  if (!text) return null;
  // Split into lines
  const lines = text.split('\n');
  const elements = [];
  let listItems = [];

  const flushList = () => {
    if (listItems.length > 0) {
      elements.push(<ul key={`ul-${elements.length}`}>{listItems}</ul>);
      listItems = [];
    }
  };

  lines.forEach((line, i) => {
    // Bullet list item: "- text"
    const bulletMatch = line.match(/^[-•]\s+(.+)/);
    if (bulletMatch) {
      listItems.push(<li key={`li-${i}`}>{parseBold(bulletMatch[1])}</li>);
      return;
    }
    flushList();

    const trimmed = line.trim();
    if (trimmed === '') {
      elements.push(<br key={`br-${i}`} />);
    } else {
      elements.push(<p key={`p-${i}`} style={{ margin: '2px 0' }}>{parseBold(trimmed)}</p>);
    }
  });
  flushList();
  return elements;
}

function parseBold(text) {
  // Convert **text** to <strong>text</strong>
  const parts = text.split(/\*\*(.+?)\*\*/g);
  if (parts.length === 1) return text;
  return parts.map((part, i) =>
    i % 2 === 1 ? <strong key={i}>{part}</strong> : part
  );
}

const ChatbotWidget = ({ apiUrl = 'http://127.0.0.1:5000/chat' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Welcome to FOSS Pulse.\n\nThe heartbeat of innovation at FOSS-CIT.\n\nExplore events, projects, and open-source opportunities.\n\nAsk. Discover. Contribute.\n\nHow can I assist you today? 🐧",
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const toggleChat = () => {
    setIsOpen(!isOpen);
    setError(null);
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputMessage }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      const botMessage = {
        id: Date.now() + 1,
        text: data.response || data.reply || 'I received your message!',
        sender: 'bot',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to send message. Please try again.');
      
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error. Please try again later.',
        sender: 'bot',
        timestamp: new Date(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearHistory = () => {
    setMessages([
      {
        id: Date.now(),
        text: "Chat history cleared. How can I help you? 🐧",
        sender: 'bot',
        timestamp: new Date()
      }
    ]);
    setError(null);
  };

  return (
    <div className="chatbot-widget">
      {/* Chat Window */}
      <div className={`chatbot-window ${isOpen ? 'open' : ''}`}>
        {/* Header */}
        <div className="chatbot-header">
          <div className="chatbot-header-content">
            <div className="chatbot-avatar">
              <img src="/penguin.svg" alt="FOSS Pulse" style={{ width: '28px', height: '28px' }} />
            </div>
            <div className="chatbot-title">
              <h3>FOSS Pulse</h3>
              <span className="chatbot-status">Online</span>
            </div>
          </div>
          <div className="chatbot-header-actions">
            <button 
              className="chatbot-clear-btn" 
              onClick={clearHistory}
              title="Clear chat history"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z" fill="currentColor"/>
              </svg>
            </button>
            <button className="chatbot-close-btn" onClick={toggleChat}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" fill="currentColor"/>
              </svg>
            </button>
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="chatbot-error-banner">
            <span>{error}</span>
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}

        {/* Messages */}
        <div className="chatbot-messages">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`chatbot-message ${message.sender === 'user' ? 'user' : 'bot'} ${message.isError ? 'error' : ''}`}
            >
              {message.sender === 'bot' && (
                <div className="message-avatar">
                  <img src="/penguin.svg" alt="FOSS Pulse" style={{ width: '24px', height: '24px' }} />
                </div>
              )}
              <div className="message-bubble">
                <div className="message-text">{message.sender === 'bot' ? renderMarkdown(message.text) : message.text}</div>
                <span className="message-time">
                  {message.timestamp.toLocaleTimeString('en-US', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </span>
              </div>
            </div>
          ))}
          
          {/* Loading Indicator */}
          {isLoading && (
            <div className="chatbot-message bot">
              <div className="message-avatar">
                <img src="/penguin.svg" alt="FOSS Pulse" style={{ width: '24px', height: '24px' }} />
              </div>
              <div className="message-bubble">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="chatbot-input-container">
          <input
            ref={inputRef}
            type="text"
            className="chatbot-input"
            placeholder="Type your message..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
          />
          <button
            className="chatbot-send-btn"
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" fill="currentColor"/>
            </svg>
          </button>
        </div>
      </div>

      {/* Floating Button */}
      <button
        className={`chatbot-toggle-btn ${isOpen ? 'hidden' : ''}`}
        onClick={toggleChat}
        aria-label="Open chat"
      >
        <img src="/penguin.svg" alt="Chat with FOSS Pulse" style={{ width: '36px', height: '36px' }} />
      </button>
    </div>
  );
};

export default ChatbotWidget;
