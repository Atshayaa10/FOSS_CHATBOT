// Example App.jsx showing integration with existing React app
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ChatbotWidget from './components/ChatbotWidget';

// Your existing components
import Home from './pages/Home';
import About from './pages/About';
import Contact from './pages/Contact';

function App() {
  return (
    <Router>
      <div className="App">
        {/* Your existing app structure */}
        <header>
          <nav>
            {/* Navigation */}
          </nav>
        </header>
        
        <main>
          {/* Your routes */}
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<About />} />
            <Route path="/contact" element={<Contact />} />
          </Routes>
        </main>
        
        <footer>
          {/* Footer content */}
        </footer>
        
        {/* 
          Add the ChatbotWidget here - it will float above all content
          No need to add it to each route or page
        */}
        <ChatbotWidget 
          apiUrl={import.meta.env.VITE_CHATBOT_API_URL || 'http://127.0.0.1:5000/chat'} 
        />
      </div>
    </Router>
  );
}

export default App;
