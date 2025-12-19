# AI Chatbot Integration Guide 🤖

## Overview
Integration of multilingual AI chatbot into the Smart Agriculture Dashboard, connected to n8n workflow for weather data and irrigation guidance.

---

## 🎯 **Chatbot Specifications**

### Core Functionality
- **Smart Assistant** for dashboard users
- **Weather & Environment Queries** with real-time data
- **Agriculture/Irrigation Guidance** based on conditions
- **Multilingual Support** (English, Tamil, Tanglish, Hindi)
- **n8n Integration** for backend data processing

### Language Detection & Response
```javascript
// Auto-detect user language and respond in same language
const detectLanguage = (message) => {
  if (/[அ-ஹ]/.test(message)) return 'tamil';
  if (/[अ-ह]/.test(message)) return 'hindi';
  if (/varuma|pannalam|irukku/i.test(message)) return 'tanglish';
  return 'english';
};
```

---

## 🔗 **n8n Webhook Integration**

### Webhook Endpoint
```
https://suryan8nproject.app.n8n.cloud/webhook/92d37ab5-1c24-4392-af50-df80c01eec93/chat
```

### Request Format
```json
{
  "message": "Iniku rain varuma?",
  "location": "Salem",
  "userId": "dashboard_user_123",
  "timestamp": "2024-12-10T10:30:00Z"
}
```

### Expected Response Format
```json
{
  "reply": "Salem-la iniku rain chance illa 🌤️ Irrigation pannalam!",
  "weather": {
    "condition": "Clear",
    "temperature": 32,
    "humidity": 65,
    "rainChance": 10
  },
  "irrigation_advice": "Medium",
  "language": "tanglish"
}
```

---

## 🎨 **Frontend Integration**

### 1. Create Chatbot Component

```typescript
// components/ChatBot.tsx
import React, { useState, useRef, useEffect } from 'react';

interface ChatMessage {
  id: string;
  message: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  language?: string;
}

interface ChatBotProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ChatBot: React.FC<ChatBotProps> = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      message: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('https://suryan8nproject.app.n8n.cloud/webhook/92d37ab5-1c24-4392-af50-df80c01eec93/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          userId: 'dashboard_user',
          timestamp: new Date().toISOString()
        })
      });

      const data = await response.json();
      
      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        message: data.reply || 'Sorry, I could not process your request.',
        sender: 'bot',
        timestamp: new Date(),
        language: data.language
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Chatbot error:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        message: 'Connection error. Please try again.',
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-4 right-4 w-80 h-96 bg-white dark:bg-slate-800 rounded-lg shadow-xl border border-slate-200 dark:border-slate-700 flex flex-col z-50">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-700">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
            🤖
          </div>
          <div>
            <h3 className="font-semibold text-slate-800 dark:text-white">Farm Assistant</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">Weather & Irrigation Help</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
        >
          ✕
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <div className="text-center text-slate-500 dark:text-slate-400 text-sm">
            <p>👋 Hi! Ask me about:</p>
            <p>• Weather updates</p>
            <p>• Irrigation advice</p>
            <p>• Crop guidance</p>
          </div>
        )}
        
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs px-3 py-2 rounded-lg text-sm ${
                msg.sender === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-slate-100 dark:bg-slate-700 text-slate-800 dark:text-white'
              }`}
            >
              {msg.message}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-slate-100 dark:bg-slate-700 px-3 py-2 rounded-lg text-sm">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-slate-200 dark:border-slate-700">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about weather, irrigation..."
            className="flex-1 px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-slate-700 dark:text-white"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !inputMessage.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};
```

### 2. Add Chatbot Toggle to Main App

```typescript
// App.tsx - Add to existing component
const [isChatOpen, setIsChatOpen] = useState(false);

// Add floating chat button
<div className="fixed bottom-4 right-4 z-40">
  {!isChatOpen && (
    <button
      onClick={() => setIsChatOpen(true)}
      className="w-14 h-14 bg-green-500 hover:bg-green-600 text-white rounded-full shadow-lg flex items-center justify-center transition-all duration-300 hover:scale-110"
    >
      🤖
    </button>
  )}
</div>

{/* Chatbot Component */}
<ChatBot isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />
```

---

## 🧠 **n8n Workflow Configuration**

### 1. Chat Trigger Node
```json
{
  "httpMethod": "POST",
  "path": "chat",
  "responseMode": "responseNode",
  "options": {}
}
```

### 2. Language Detection Node (Code)
```javascript
// Detect user language
const message = $json.message.toLowerCase();
let language = 'english';

if (/[அ-ஹ]/.test(message)) {
  language = 'tamil';
} else if (/[अ-ह]/.test(message)) {
  language = 'hindi';
} else if (/varuma|pannalam|irukku|iniku|nalla/i.test(message)) {
  language = 'tanglish';
}

// Extract location if mentioned
const locationMatch = message.match(/(?:in |la |il )?([a-zA-Z\s]+)(?:\s|$)/);
const location = locationMatch ? locationMatch[1].trim() : null;

return {
  message: $json.message,
  language: language,
  location: location,
  userId: $json.userId,
  timestamp: $json.timestamp
};
```

### 3. Weather API Node (HTTP Request)
```json
{
  "method": "GET",
  "url": "https://api.openweathermap.org/data/2.5/weather",
  "qs": {
    "q": "={{$json.location || 'Salem'}}",
    "appid": "YOUR_API_KEY",
    "units": "metric"
  }
}
```

### 4. Response Generation Node (Code)
```javascript
const { language, message } = $('Language Detection').first().json;
const weather = $('Weather API').first().json;

// Weather condition mapping
const condition = weather.weather[0].main;
const temp = Math.round(weather.main.temp);
const humidity = weather.main.humidity;
const rainChance = weather.rain ? 80 : 20;

// Irrigation advice logic
let irrigationAdvice = 'Medium';
if (condition === 'Rain' || rainChance > 70) {
  irrigationAdvice = 'None';
} else if (temp > 35 && humidity < 40) {
  irrigationAdvice = 'High';
} else if (temp < 25 || humidity > 80) {
  irrigationAdvice = 'Low';
}

// Generate response based on language
let reply = '';
const endings = {
  tamil: 'மேலும் உதவி வேண்டுமா 🙂',
  hindi: 'और मदद चाहिए तो बताइए 🙂',
  english: 'Let me know if you need more help 🙂',
  tanglish: 'Let me know if you need more help 🙂'
};

if (language === 'tamil') {
  if (condition === 'Rain') {
    reply = `இன்று மழை வரும் 🌧️ நீர்ப்பாசனம் வேண்டாம்! ${endings.tamil}`;
  } else {
    reply = `இன்று வானிலை: ${temp}°C 🌤️ நீர்ப்பாசனம்: ${irrigationAdvice === 'High' ? 'அதிகம்' : irrigationAdvice === 'Low' ? 'குறைவு' : 'நடுத்தரம்'} ${endings.tamil}`;
  }
} else if (language === 'hindi') {
  if (condition === 'Rain') {
    reply = `आज बारिश होगी 🌧️ सिंचाई की जरूरत नहीं! ${endings.hindi}`;
  } else {
    reply = `आज का मौसम: ${temp}°C 🌤️ सिंचाई: ${irrigationAdvice === 'High' ? 'ज्यादा' : irrigationAdvice === 'Low' ? 'कम' : 'मध्यम'} ${endings.hindi}`;
  }
} else if (language === 'tanglish') {
  if (condition === 'Rain') {
    reply = `Iniku rain varum 🌧️ Irrigation vendam! ${endings.tanglish}`;
  } else {
    reply = `Iniku weather: ${temp}°C 🌤️ Irrigation: ${irrigationAdvice} pannalam ${endings.tanglish}`;
  }
} else {
  if (condition === 'Rain') {
    reply = `Rain expected today 🌧️ Skip irrigation! ${endings.english}`;
  } else {
    reply = `Today's weather: ${temp}°C 🌤️ Irrigation: ${irrigationAdvice} recommended ${endings.english}`;
  }
}

return {
  reply: reply,
  weather: {
    condition: condition,
    temperature: temp,
    humidity: humidity,
    rainChance: rainChance
  },
  irrigation_advice: irrigationAdvice,
  language: language
};
```

### 5. Response Node
```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*"
  }
}
```

---

## 📱 **Mobile Optimization**

### Responsive Design
```css
/* Mobile-first chatbot styling */
@media (max-width: 640px) {
  .chatbot-container {
    position: fixed;
    bottom: 0;
    right: 0;
    left: 0;
    width: 100%;
    height: 70vh;
    border-radius: 16px 16px 0 0;
  }
  
  .chat-toggle-button {
    bottom: 20px;
    right: 20px;
    width: 56px;
    height: 56px;
  }
}
```

### Touch Interactions
```typescript
// Add touch-friendly interactions
const handleTouchStart = (e: TouchEvent) => {
  // Handle touch gestures for mobile
};
```

---

## 🌐 **Multilingual Examples**

### Sample Conversations

#### English
```
User: "What's the weather in Salem today?"
Bot: "Today's weather: 32°C 🌤️ Irrigation: Medium recommended. Let me know if you need more help 🙂"
```

#### Tamil
```
User: "இன்று சேலத்தில் மழை வருமா?"
Bot: "இன்று மழை வராது 🌤️ நீர்ப்பாசனம் நடுத்தரம் செய்யலாம். மேலும் உதவி வேண்டுமா 🙂"
```

#### Tanglish
```
User: "Iniku rain varuma Salem-la?"
Bot: "Iniku rain chance illa 🌤️ Irrigation medium pannalam. Let me know if you need more help 🙂"
```

#### Hindi
```
User: "आज सेलम में बारिश होगी क्या?"
Bot: "आज बारिश नहीं होगी 🌤️ सिंचाई मध्यम करें। और मदद चाहिए तो बताइए 🙂"
```

---

## 🔧 **Integration Steps**

### 1. Add Chatbot to Dashboard
```bash
# Add chatbot component to existing project
npm install # (no additional dependencies needed)
```

### 2. Update App.tsx
```typescript
import { ChatBot } from './components/ChatBot';

// Add chatbot state and UI elements
```

### 3. Configure n8n Workflow
- Set up webhook endpoint
- Add weather API integration
- Configure language detection
- Test response generation

### 4. Test Integration
```bash
# Test chatbot in development
npm run dev

# Test n8n webhook
curl -X POST https://suryan8nproject.app.n8n.cloud/webhook/92d37ab5-1c24-4392-af50-df80c01eec93/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Weather today?", "userId": "test"}'
```

---

## 🚀 **Deployment Considerations**

### Environment Variables
```bash
# Add to .env.local
VITE_N8N_WEBHOOK_URL=https://suryan8nproject.app.n8n.cloud/webhook/92d37ab5-1c24-4392-af50-df80c01eec93/chat
VITE_CHATBOT_ENABLED=true
```

### Error Handling
```typescript
// Graceful fallback for offline/error states
const fallbackResponse = {
  english: "I'm having trouble connecting. Please try again later. Let me know if you need more help 🙂",
  tamil: "இணைப்பில் சிக்கல். மீண்டும் முயற்சிக்கவும். மேலும் உதவி வேண்டுமா 🙂",
  hindi: "कनेक्शन में समस्या है। कृपया बाद में कोशिश करें। और मदद चाहिए तो बताइए 🙂",
  tanglish: "Connection problem. Try again later. Let me know if you need more help 🙂"
};
```

---

## ✅ **Features Summary**

### Core Capabilities
- ✅ **Multilingual Support** (4 languages)
- ✅ **Weather Integration** via n8n
- ✅ **Irrigation Advice** based on conditions
- ✅ **Mobile Responsive** design
- ✅ **Real-time Chat** interface
- ✅ **Error Handling** and fallbacks

### Smart Features
- ✅ **Auto Language Detection**
- ✅ **Location Extraction** from messages
- ✅ **Context-Aware Responses**
- ✅ **Emoji Integration** for better UX
- ✅ **Typing Indicators** for engagement

---

## 🎯 **Next Steps**

1. **Implement ChatBot Component** in React
2. **Set up n8n Workflow** with weather API
3. **Test Multilingual Responses** 
4. **Integrate with Dashboard** UI
5. **Deploy and Monitor** performance

The chatbot will enhance the Smart Agriculture Dashboard by providing intelligent, multilingual assistance for weather queries and irrigation guidance! 🚀