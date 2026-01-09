# Daily Weather Email Automation Feature

## 📧 Current Configuration

**Recipients:**
- ***REMOVED***
- ***REMOVED***

**Schedule:**
- **Morning Report**: 6:00 AM IST daily
- **Evening Report**: 7:00 PM IST daily

**Location:** Erode, Tamil Nadu, India

## 🌟 Features

- **Twice Daily Emails**: Morning (6:00 AM) and Evening (7:00 PM) IST
- **Weather Data**: Temperature, humidity, rain probability, and conditions for Erode, Tamil Nadu
- **Smart Irrigation Recommendations**: AI-powered decision making for irrigation
- **Beautiful HTML Emails**: Responsive design with green agriculture theme
- **Rain Alerts**: Warning banners when rain is expected
- **Time-Specific Content**: Different greetings and content for morning vs evening
- **Independent Operation**: Runs separately without affecting main application

## 📁 Files Created

### Core Service Files
- `dailyWeatherEmail.service.js` - Node.js version of the service
- `daily_weather_email_service.py` - Python version of the service
- `weather_email_integration.py` - Auto-integration module for Python backend

### Configuration & Setup
- `.env.example` - Environment variables template
- `initDailyWeatherEmail.js` - Node.js initialization module
- `start_weather_email_service.py` - Standalone Python starter

### Testing & Utilities
- `testDailyWeatherEmail.js` - Node.js test script
- `test_daily_weather_email.py` - Python test script
- `send_test_emails.py` - Send immediate test emails to configured recipients
- `start_weather_emails.py` - Start service with pre-configured recipients

## 🚀 Quick Setup

### 1. Install Dependencies

**For Node.js version:**
```bash
npm install node-cron nodemailer axios dotenv
```

**For Python version:**
```bash
pip install aiohttp schedule
```

### 2. Configure Email Settings

Create a `.env.local` file with your email credentials:

```env
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
EMAIL_RECIPIENTS=farmer1@example.com,farmer2@example.com

# Weather API (reuses existing key)
OPENWEATHER_API_KEY=***REMOVED***
```

### 3. Integration Options

#### Option A: Auto-Integration with Python Backend
Add this single line to your `backend.py`:
```python
import weather_email_integration  # Add at the end of backend.py
```

#### Option B: Standalone Service
**Python:**
```bash
python start_weather_email_service.py
```

**Node.js:**
```bash
node initDailyWeatherEmail.js
```

## 🧪 Testing

### Test Python Version
```bash
python test_daily_weather_email.py
```

### Test Node.js Version
```bash
node testDailyWeatherEmail.js
```

## 📧 Email Features

### Email Content
- **Header**: Green gradient with Smart Agriculture branding
- **Greeting**: "Good Morning ☀️ Have a nice day and a successful farming day ahead."
- **Weather Card**: Temperature, humidity, conditions, rain probability
- **Rain Alert**: Red warning banner when rain probability > 50%
- **Irrigation Recommendation**: Yes/No with reasoning
- **Footer**: System branding and location

### Responsive Design
- Mobile-friendly layout
- Green agriculture theme (light green → dark green gradient)
- Weather icons from OpenWeatherMap
- Clean, professional styling

## 🤖 Smart Logic

### Rain Alert Conditions
- Rain probability > 50% OR
- Current weather shows rain

### Irrigation Recommendations
- **Good for irrigation**: Rain probability ≤ 30% AND humidity < 70%
- **Not recommended**: Rain alert OR high humidity/rain chance

## ⏰ Scheduling

- **Daily Schedule**: 6:30 AM IST (1:00 AM UTC)
- **Timezone**: Asia/Kolkata
- **Cron Expression**: `0 1 * * *`

## 🔧 Configuration Options

### Environment Variables
```env
# Required
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
EMAIL_RECIPIENTS=recipient1@email.com,recipient2@email.com

# Optional
SMTP_HOST=smtp.gmail.com          # Default: smtp.gmail.com
SMTP_PORT=587                     # Default: 587
WEATHER_CITY=Erode,Tamil Nadu,IN  # Default: Erode,Tamil Nadu,IN
OPENWEATHER_API_KEY=your-key      # Reuses existing key
```

### Gmail Setup
1. Enable 2-Factor Authentication
2. Generate App Password: Google Account → Security → App passwords
3. Use the app password in `EMAIL_PASS`

## 🛡️ Safety Features

- **Error Isolation**: Failures don't affect main Smart Agriculture application
- **Graceful Degradation**: Service continues even if email fails
- **Daemon Threads**: Background operation without blocking main app
- **Comprehensive Logging**: Detailed status messages for debugging

## 📊 Sample Email Output

```
🌱 Daily Weather Report
Friday, January 10, 2025

Good Morning ☀️
Have a nice day and a successful farming day ahead.

📍 Erode
Temperature: 23°C
Humidity: 63%
Condition: Broken clouds
Rain Chance: 0%

🚿 Is today good for irrigation?
Yes
Good for irrigation

Smart Agriculture System | Location: Erode, Tamil Nadu
```

## 🔍 Troubleshooting

### Common Issues

1. **Email not sending**
   - Check email credentials in `.env.local`
   - Verify Gmail app password setup
   - Check SMTP settings

2. **Weather data not fetching**
   - Verify OpenWeather API key
   - Check internet connection
   - Confirm API rate limits

3. **Service not starting**
   - Check Python/Node.js dependencies
   - Verify file permissions
   - Review error logs

### Debug Commands

**Test weather fetch:**
```bash
python test_daily_weather_email.py
```

**Test email generation:**
```bash
node testDailyWeatherEmail.js
```

**Manual email send:**
Uncomment test email lines in test scripts

## 🎯 Integration Examples

### With FastAPI Backend
```python
# At the end of backend.py
try:
    import weather_email_integration
    print("✅ Daily Weather Email Service integrated")
except Exception as e:
    print(f"⚠️ Weather email service not available: {e}")
```

### Standalone Service
```bash
# Run as separate service
python start_weather_email_service.py &
```

### Docker Integration
```dockerfile
# Add to your Dockerfile
COPY daily_weather_email_service.py .
COPY weather_email_integration.py .
RUN pip install aiohttp schedule
```

## 📈 Future Enhancements

- Multiple city support
- Custom email templates
- Weather alerts for extreme conditions
- Integration with SMS notifications
- Historical weather data analysis
- Crop-specific recommendations

## 🤝 Support

This feature is designed to be completely independent. If you encounter issues:

1. Check the test scripts first
2. Verify environment configuration
3. Review error logs
4. The main Smart Agriculture system will continue working regardless

## 📝 License

This feature follows the same license as your main Smart Agriculture project.

---

**Note**: This feature is completely separate from your existing Smart Agriculture functionality. It can be safely added, removed, or modified without affecting any existing features.