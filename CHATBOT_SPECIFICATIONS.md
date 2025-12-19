# Smart Agriculture Dashboard AI Chatbot Specifications 🤖🌾

## Core Requirements Summary

### 🎯 **Primary Function**
- Answer farmer questions about weather and irrigation
- Use ONLY n8n backend data (OpenWeather APIs)
- Never guess or hallucinate weather information
- Provide accurate, real-time agricultural guidance

---

## 🌐 **Language Support (STRICT RULES)**

### Supported Languages
1. **Tamil** (தமிழ்) - Native Tamil script
2. **English** - Standard English
3. **Tanglish** - Tamil written in English letters
4. **Hindi** (हिंदी) - Devanagari script

### Language Rules
```
✅ DO:
- Detect user's language automatically
- Reply in EXACT SAME language
- Keep language pure (no mixing)

❌ DON'T:
- Mix languages in responses
- Translate unless asked
- Change language mid-conversation
```

### Examples
```
Tamil Input: "இன்று மழை வருமா?"
Tamil Output: "இன்று மழை வராது 🌤️"

English Input: "Will it rain today?"
English Output: "No rain expected today 🌤️"

Tanglish Input: "Iniku mala varuma?"
Tanglish Output: "Iniku mala varadu 🌤️"

Hindi Input: "आज बारिश होगी?"
Hindi Output: "आज बारिश नहीं होगी 🌤️"
```

---

## 📅 **Date & Weather Logic (CRITICAL)**

### TODAY Questions
**Keywords**: "today", "iniku", "இன்னைக்கு", "aaj"

```javascript
// Use ONLY current weather data from n8n
if (weather.main === "Rain") {
  // Rain will come
} else if (weather.main === "Clear" || weather.main === "Clouds") {
  // No rain expected
}
```

### TOMORROW Questions  
**Keywords**: "tomorrow", "naalai", "நாளை", "kal"

```javascript
// Use ONLY forecast data from n8n
if (forecastData.available) {
  // Process forecast data
} else {
  // "Tomorrow weather data is not available right now."
}
```

### Rain Decision Matrix
| weather.main | Decision | Response |
|--------------|----------|----------|
| "Rain" | Rain expected | "மழை வரும்" / "Rain expected" |
| "Drizzle" | Light rain | "லேசான மழை" / "Light rain" |
| "Clear" | No rain | "மழை வராது" / "No rain" |
| "Clouds" | No rain | "மழை வராது" / "No rain" |

---

## 💧 **Irrigation Logic**

### Decision Tree
```
if (rain_expected) {
  advice = "Do NOT irrigate"
} else if (temperature > 35°C && humidity < 40%) {
  advice = "High irrigation needed"
} else if (temperature < 25°C || humidity > 80%) {
  advice = "Low irrigation"
} else {
  advice = "Medium irrigation"
}
```

### Multilingual Irrigation Advice
| Level | Tamil | English | Tanglish | Hindi |
|-------|-------|---------|----------|-------|
| None | நீர்ப்பாசனம் வேண்டாம் | Do not irrigate | Irrigation vendam | सिंचाई न करें |
| Low | குறைவு | Low irrigation | Konjam irrigation | कम सिंचाई |
| Medium | நடுத்தரம் | Medium irrigation | Medium irrigation | मध्यम सिंचाई |
| High | அதிகம் | High irrigation | Adhigam irrigation | ज्यादा सिंचाई |

---

## 💬 **Response Style Guidelines**

### Format Requirements
- ✅ **Short sentences** - Easy to read on mobile
- ✅ **Bullet points** - Clear information structure
- ✅ **Farmer-friendly language** - Simple, practical terms
- ✅ **Light emojis** - 🌦️🌱💧 for visual appeal
- ❌ **No raw JSON** - Hide technical details
- ❌ **No "checking weather"** - Give direct answers
- ❌ **No "please wait"** - Provide immediate responses

### Response Structure
```
Weather Information:
🌡️ Temperature
💧 Humidity  
🌤️ Condition
💧 Irrigation Advice
🙂 Help Ending
```

---

## 🔚 **End Messages (Language-Specific)**

### Required Endings
```javascript
const endings = {
  tamil: "மேலும் உதவி வேண்டுமா 🙂",
  english: "Let me know if you need more help 🙂", 
  tanglish: "Innum help venuma 🙂",
  hindi: "और मदद चाहिए तो बताइए 🙂"
};
```

---

## 🎯 **Sample Conversations**

### Tamil Weather Query
```
User: "இன்று சேலத்தில் மழை வருமா?"
Bot: "சேலத்தில் இன்று மழை வராது 🌤️
🌡️ 28°C
💧 65% ஈரப்பதம்
நீர்ப்பாசனம்: நடுத்தரம்
மேலும் உதவி வேண்டுமா 🙂"
```

### English Weather Query
```
User: "Weather today in Salem?"
Bot: "Salem weather today: Clear sky 🌤️
🌡️ 28°C
💧 65% humidity
Irrigation: Medium recommended
Let me know if you need more help 🙂"
```

### Tanglish Weather Query
```
User: "Iniku mala varuma Salem-la?"
Bot: "Salem-la iniku mala varadu 🌤️
🌡️ 28°C
💧 65% humidity
Irrigation: Medium pannalam
Innum help venuma 🙂"
```

### Hindi Weather Query
```
User: "आज सेलम में बारिश होगी?"
Bot: "सेलम में आज बारिश नहीं होगी 🌤️
🌡️ 28°C
💧 65% नमी
सिंचाई: मध्यम करें
और मदद चाहिए तो बताइए 🙂"
```

---

## ⚠️ **Critical Don'ts**

### Weather Information
- ❌ **Never guess weather** - Only use n8n API data
- ❌ **Don't use today's data for tomorrow** - Wait for forecast
- ❌ **Don't say "rain will come"** unless API confirms
- ❌ **Don't show raw API responses** - Process and format

### Language Handling
- ❌ **Don't mix languages** - Keep responses pure
- ❌ **Don't auto-translate** - Respond in input language
- ❌ **Don't assume language** - Detect from user input

### User Experience
- ❌ **Don't say "checking"** - Give direct answers
- ❌ **Don't use technical terms** - Keep farmer-friendly
- ❌ **Don't give long responses** - Keep concise and clear

---

## 🔧 **Technical Implementation**

### n8n Integration
```javascript
// Request format
{
  "action": "sendMessage",
  "chatInput": userMessage,
  "sessionId": "farmer-session-1"
}

// Expected response
{
  "output": "Formatted weather response with irrigation advice"
}
```

### Language Detection
```javascript
const detectLanguage = (message) => {
  if (/[அ-ஹ]/.test(message)) return 'tamil';
  if (/[अ-ह]/.test(message)) return 'hindi';
  if (/iniku|mala|varuma|pannalam|la|ku/i.test(message)) return 'tanglish';
  return 'english';
};
```

### Response Processing
```javascript
// Use n8n output directly (already formatted)
if (data.output) {
  botReply = data.output;
} else {
  botReply = "No response from assistant";
}
```

---

## 🎯 **Success Criteria**

### Accuracy Requirements
- ✅ **100% API-based responses** - No guessing
- ✅ **Language consistency** - Pure language responses  
- ✅ **Date accuracy** - Today vs tomorrow distinction
- ✅ **Irrigation relevance** - Weather-based advice

### User Experience Goals
- ✅ **Fast responses** - < 2 seconds
- ✅ **Clear information** - Easy to understand
- ✅ **Mobile-friendly** - Readable on small screens
- ✅ **Farmer-focused** - Practical agricultural advice

---

## 🚀 **Current Status**

### ✅ Implemented Features
- n8n webhook integration
- Multilingual support (4 languages)
- Professional chat interface
- Weather data processing
- Irrigation advice logic
- Responsive design

### ✅ Ready for Production
- Real weather data integration
- Accurate language detection
- Proper response formatting
- Error handling and fallbacks
- Mobile-optimized interface

**The Smart Agriculture Dashboard AI Chatbot is production-ready with all specifications implemented! 🌾🤖✨**