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

  // Initialize with welcome message
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      const welcomeMessage: ChatMessage = {
        id: 'welcome',
        message: '👋 Hi! I can help you with:\n• Weather updates 🌤️\n• Irrigation advice 💧\n• Crop guidance 🌱\n\nAsk me in English, Tamil, Hindi, or Tanglish!\nExample: "Iniku mala varuma?" or "Weather today?"',
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
    }
  }, [isOpen, messages.length]);

  const detectLanguage = (message: string): string => {
    const msg = message.toLowerCase();
    if (/[அ-ஹ]/.test(message)) return 'tamil';
    if (/[अ-ह]/.test(message)) return 'hindi';
    // Enhanced Tanglish detection
    if (/varuma|pannalam|irukku|iniku|nalla|mala|eppo|enna|sollu|podu|vidu|varen|poren|vandhen|pochu|achu|illa|iruku|pannu|seiyya|kedachu|kedaikum|kedaika|kedaikala|kedaikadhu|vendum|vendam|venum|la|il|ku|da|di|le|lo|ki|ko|na|nu|ne|no/i.test(msg)) return 'tanglish';
    return 'english';
  };

  const getFallbackResponse = (language: string): string => {
    const responses = {
      tamil: 'மன்னிக்கவும், இணைப்பில் சிக்கல். மீண்டும் முயற்சிக்கவும். மேலும் உதவி வேண்டுமா 🙂',
      hindi: 'माफ़ करें, कनेक्शन में समस्या है। कृपया बाद में कोशिश करें। और मदद चाहिए तो बताइए 🙂',
      tanglish: 'Sorry, connection problem. Try again later. Let me know if you need more help 🙂',
      english: 'Sorry, I\'m having trouble connecting. Please try again later. Let me know if you need more help 🙂'
    };
    return responses[language as keyof typeof responses] || responses.english;
  };

  const processWeatherData = (weatherData: any, language: string, originalMessage: string): string => {
    if (!weatherData || !weatherData.main) {
      return getFallbackResponse(language);
    }

    const temp = Math.round(weatherData.main.temp - 273.15); // Convert Kelvin to Celsius
    const humidity = weatherData.main.humidity;
    const condition = weatherData.weather?.[0]?.main || 'Unknown';
    const description = weatherData.weather?.[0]?.description || '';
    const location = weatherData.name || 'your area';

    // Determine if it's raining
    const isRaining = condition === 'Rain' || condition === 'Drizzle' || condition === 'Thunderstorm';
    
    // Irrigation advice
    let irrigationAdvice = 'Medium';
    if (isRaining) {
      irrigationAdvice = 'None';
    } else if (temp > 35 && humidity < 40) {
      irrigationAdvice = 'High';
    } else if (temp < 25 || humidity > 80) {
      irrigationAdvice = 'Low';
    }

    // Generate response based on language
    const endings = {
      tamil: 'மேலும் உதவி வேண்டுமா 🙂',
      hindi: 'और मदद चाहिए तो बताइए 🙂',
      english: 'Let me know if you need more help 🙂',
      tanglish: 'Let me know if you need more help 🙂'
    };

    let reply = '';
    
    if (language === 'tamil') {
      if (isRaining) {
        reply = `${location}-ல் இன்று மழை 🌧️ (${temp}°C)\nநீர்ப்பாசனம் வேண்டாம்!\n${endings.tamil}`;
      } else {
        const irrigationTamil = irrigationAdvice === 'High' ? 'அதிகம்' : irrigationAdvice === 'Low' ? 'குறைவு' : 'நடுத்தரம்';
        reply = `${location}-ல் இன்று வானிலை:\n🌡️ ${temp}°C, 💧 ${humidity}%\n🌤️ ${description}\nநீர்ப்பாசனம்: ${irrigationTamil}\n${endings.tamil}`;
      }
    } else if (language === 'hindi') {
      if (isRaining) {
        reply = `${location} में आज बारिश 🌧️ (${temp}°C)\nसिंचाई की जरूरत नहीं!\n${endings.hindi}`;
      } else {
        const irrigationHindi = irrigationAdvice === 'High' ? 'ज्यादा' : irrigationAdvice === 'Low' ? 'कम' : 'मध्यम';
        reply = `${location} में आज का मौसम:\n🌡️ ${temp}°C, 💧 ${humidity}%\n🌤️ ${description}\nसिंचाई: ${irrigationHindi}\n${endings.hindi}`;
      }
    } else if (language === 'tanglish') {
      if (isRaining) {
        reply = `${location}-la iniku mala 🌧️ (${temp}°C)\nIrrigation vendam!\n${endings.tanglish}`;
      } else {
        reply = `${location}-la iniku weather:\n🌡️ ${temp}°C, 💧 ${humidity}%\n🌤️ ${description}\nIrrigation: ${irrigationAdvice} pannalam\n${endings.tanglish}`;
      }
    } else {
      if (isRaining) {
        reply = `${location} weather today: Rain 🌧️ (${temp}°C)\nSkip irrigation!\n${endings.english}`;
      } else {
        reply = `${location} weather today:\n🌡️ ${temp}°C, 💧 ${humidity}%\n🌤️ ${description}\nIrrigation: ${irrigationAdvice} recommended\n${endings.english}`;
      }
    }

    return reply;
  };

  const getLocalResponse = (message: string, language: string): string | null => {
    const msg = message.toLowerCase();
    
    // Simple local responses for common queries
    if (msg.includes('hello') || msg.includes('hi') || msg.includes('vanakkam') || msg.includes('namaste')) {
      const greetings = {
        tamil: 'வணக்கம்! எப்படி உதவ முடியும்? மேலும் உதவி வேண்டுமா 🙂',
        hindi: 'नमस्ते! कैसे मदद कर सकता हूँ? और मदद चाहिए तो बताइए 🙂',
        tanglish: 'Vanakkam! How can I help you? Let me know if you need more help 🙂',
        english: 'Hello! How can I help you today? Let me know if you need more help 🙂'
      };
      return greetings[language as keyof typeof greetings] || greetings.english;
    }

    if (msg.includes('thank') || msg.includes('nandri') || msg.includes('dhanyawad')) {
      const thanks = {
        tamil: 'வரவேற்கிறேன்! மேலும் உதவி வேண்டுமா 🙂',
        hindi: 'आपका स्वागत है! और मदद चाहिए तो बताइए 🙂',
        tanglish: 'Welcome! Let me know if you need more help 🙂',
        english: 'You\'re welcome! Let me know if you need more help 🙂'
      };
      return thanks[language as keyof typeof thanks] || thanks.english;
    }

    // Let weather queries go to n8n instead of providing local responses

    return null;
  };

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      message: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentMessage = inputMessage;
    setInputMessage('');
    setIsLoading(true);

    try {
      const language = detectLanguage(currentMessage);
      
      // Check for local responses first
      const localResponse = getLocalResponse(currentMessage, language);
      if (localResponse) {
        const botMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          message: localResponse,
          sender: 'bot',
          timestamp: new Date(),
          language: language
        };
        setMessages(prev => [...prev, botMessage]);
        setIsLoading(false);
        return;
      }

      // Try N8N webhook first, fallback to clean weather responses
      let botReply = '';
      let useLocalBackend = false;
      
      try {
        const webhookUrl = import.meta.env.VITE_N8N_WEBHOOK_URL || "https://suryan8nproject.app.n8n.cloud/webhook/ccd37962-6bb3-4c30-b859-d3b63b9c64e2/chat";
        
        // Create timeout promise for better browser compatibility
        const timeoutPromise = new Promise((_, reject) => 
          setTimeout(() => reject(new Error('N8N request timeout')), 3000) // Reduced to 3 seconds
        );
        
        const fetchPromise = fetch(webhookUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            sessionId: "agri-dashboard",
            action: "sendMessage",
            chatInput: currentMessage,
            language: language
          })
        });
        
        const response = await Promise.race([fetchPromise, timeoutPromise]) as Response;

        if (!response.ok) {
          throw new Error(`N8N HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log("N8N RAW RESPONSE:", data);
        
        if (data.output) {
          botReply = data.output;
        } else if (data.coord && data.main && data.weather) {
          botReply = processWeatherData(data, language, currentMessage);
        } else {
          throw new Error("Invalid N8N response format");
        }
      } catch (n8nError) {
        console.log("N8N failed, using clean weather fallback:", n8nError);
        useLocalBackend = true;
      }

      // Fallback to clean weather responses using local API
      if (useLocalBackend) {
      
      try {
        const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
        console.log("Using local backend:", apiUrl);
          
          // Check if it's a weather query
          const isWeatherQuery = /weather|mala|rain|varuma|temperature|temp|climate|hot|cold|sunny|cloudy|irrigation.*advice/i.test(currentMessage);
          console.log("Is weather query:", isWeatherQuery, "for message:", currentMessage);
          
          if (isWeatherQuery) {
            console.log("Fetching weather from:", `${apiUrl}/weather`);
            const weatherResponse = await fetch(`${apiUrl}/weather`, {
              method: "GET",
              headers: { "Content-Type": "application/json" }
            });
            
            console.log("Weather response status:", weatherResponse.status);
            
            if (weatherResponse.ok) {
              const weatherData = await weatherResponse.json();
              console.log("Weather data received:", weatherData);
              
              botReply = (() => {
                const temp = Math.round(weatherData.temperature);
                const humidity = weatherData.humidity;
                const rainProb = Math.round(weatherData.rain_probability);
                const location = weatherData.location;
                
                // Simple, clean responses as requested
                if (language === 'tamil') {
                  return `${location}-la iniku weather: 🌡️ ${temp}°C, 💧 ${humidity}% 🌧️ மழை வாய்ப்பு: ${rainProb}% நீர்ப்பாசனம் செய்யலாம். மேலும் உதவி வேண்டுமா 🙂`;
                } else if (language === 'tanglish') {
                  return `${location}-la iniku weather: 🌡️ ${temp}°C, 💧 ${humidity}% 🌧️ Rain chance: ${rainProb}% Irrigation pannalam. Let me know if you need more help 🙂`;
                } else {
                  return `${location} weather today: 🌡️ ${temp}°C, 💧 ${humidity}% 🌧️ Rain chance: ${rainProb}% Irrigation recommended. Let me know if you need more help 🙂`;
                }
              })();
            } else {
              console.error("Weather API failed with status:", weatherResponse.status);
              throw new Error(`Weather API failed: ${weatherResponse.status}`);
            }
          } else {
            // For non-weather queries, provide general agricultural advice
            const generalResponses = {
              tamil: 'வேளாண்மை குறித்த கேள்விகளுக்கு உதவ தயாராக இருக்கிறேன். வானிலை, நீர்ப்பாசனம், பயிர் வளர்ப்பு பற்றி கேளுங்கள். மேலும் உதவி வேண்டுமா 🙂',
              tanglish: 'Agriculture questions ku help pannalam. Weather, irrigation, crop growing pathi kelunga. Let me know if you need more help 🙂',
              english: 'I can help with agriculture questions. Ask about weather, irrigation, or crop growing. Let me know if you need more help 🙂'
            };
            botReply = generalResponses[language as keyof typeof generalResponses] || generalResponses.english;
          }
        } catch (localError) {
          console.error("Local backend failed:", localError);
          botReply = getFallbackResponse(language);
        }
      }
      
      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        message: botReply,
        sender: 'bot',
        timestamp: new Date(),
        language: language
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Chatbot error:', error);
      const language = detectLanguage(currentMessage);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        message: getFallbackResponse(language),
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
    <>
      {/* Mobile backdrop */}
      <div className="fixed inset-0 bg-black bg-opacity-50 z-40 sm:hidden" onClick={onClose} />
      
      {/* Chatbot container */}
      <div className="fixed bottom-0 right-0 sm:bottom-4 sm:right-4 w-full h-[75vh] sm:w-96 sm:h-[500px] bg-white dark:bg-slate-800 sm:rounded-lg shadow-xl border-t sm:border border-slate-200 dark:border-slate-700 flex flex-col z-50">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-700 bg-gradient-to-r from-green-500 to-blue-500 text-white sm:rounded-t-lg">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <div>
              <h3 className="font-semibold">Farm Assistant</h3>
              <p className="text-xs opacity-90">Weather & Irrigation Help</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:text-gray-200 text-xl font-bold w-8 h-8 flex items-center justify-center rounded-full hover:bg-white hover:bg-opacity-20 transition-all duration-200"
          >
            ×
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50 dark:bg-slate-900">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] px-4 py-2 rounded-2xl text-sm leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-blue-500 text-white rounded-br-md'
                    : 'bg-white dark:bg-slate-700 text-slate-800 dark:text-white rounded-bl-md shadow-sm'
                }`}
              >
                <div className="whitespace-pre-line">{msg.message}</div>
                <div className={`text-xs mt-1 opacity-70 ${
                  msg.sender === 'user' ? 'text-blue-100' : 'text-slate-500 dark:text-slate-400'
                }`}>
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white dark:bg-slate-700 px-4 py-3 rounded-2xl rounded-bl-md shadow-sm">
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
        <div className="p-4 border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800">
          <div className="flex space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about weather, irrigation..."
              className="flex-1 px-4 py-2 border border-slate-300 dark:border-slate-600 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-slate-700 dark:text-white transition-all duration-200"
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !inputMessage.trim()}
              className="px-6 py-2 bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-full text-sm font-medium hover:from-green-600 hover:to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-sm"
            >
              Send
            </button>
          </div>
          
          {/* Quick suggestions */}
          <div className="flex flex-wrap gap-2 mt-2">
            <button
              onClick={() => setInputMessage('Weather today?')}
              className="px-3 py-1 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 rounded-full text-xs hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
              disabled={isLoading}
            >
              Weather today?
            </button>
            <button
              onClick={() => setInputMessage('Iniku mala varuma?')}
              className="px-3 py-1 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 rounded-full text-xs hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
              disabled={isLoading}
            >
              Iniku mala varuma?
            </button>
            <button
              onClick={() => setInputMessage('Irrigation advice?')}
              className="px-3 py-1 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 rounded-full text-xs hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
              disabled={isLoading}
            >
              Irrigation advice?
            </button>
          </div>
        </div>
      </div>
    </>
  );
};