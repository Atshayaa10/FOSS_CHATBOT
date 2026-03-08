import React from 'react';
import ChatbotWidget from './components/ChatbotWidget';
import './App.css';

function App() {
  return (
    <div className="App">
      {/* Chatbot Widget - Only component on the page */}
      <ChatbotWidget apiUrl="http://127.0.0.1:5000/chat" />
    </div>
  );
}

export default App;
