# Smart Agriculture Dashboard - Production Deployment Guide

## 🚀 DEPLOYMENT OVERVIEW

This guide covers the complete production deployment of the Smart Agriculture Dashboard across multiple platforms:

- **Frontend**: React + TypeScript → Vercel
- **Backend**: FastAPI + WebSocket → Render
- **Database**: Supabase (PostgreSQL)
- **External Services**: OpenWeather API, Telegram Bot API, n8n Automation

---

## 📋 PRE-DEPLOYMENT CHECKLIST

### 1. Environment Variables Setup
Create accounts and obtain API keys for:

- [ ] **Supabase**: Database URL and Service Role Key
- [ ] **OpenWeather API**: API Key from openweathermap.org
- [ ] **Telegram Bot**: Bot Token from @BotFather
- [ ] **n8n**: Webhook URL for chatbot integration
- [ ] **Render**: Account for backend hosting
- [ ] **Vercel**: Account for frontend hosting

### 2. Database Setup (Supabase)
1. Create new Supabase project
2. Run the SQL schema from `database/supabase-schema.sql`
3. Configure Row Level Security (RLS) policies
4. Note down the project URL and service role key

### 3. Code Preparation
- [ ] All localhost URLs replaced with environment variables
- [ ] API keys moved to environment variables
- [ ] Production error handling implemented
- [ ] Database integration completed
- [ ] SSL/WSS configuration ready

---

## 🗄️ DATABASE DEPLOYMENT (SUPABASE)

### Step 1: Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Choose region (closest to your users)
4. Set strong database password

### Step 2: Run Database Schema
1. Open Supabase SQL Editor
2. Copy and paste content from `database/supabase-schema.sql`
3. Execute the script to create all tables and indexes
4. Verify tables are created successfully

### Step 3: Configure Environment Variables
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

### Step 4: Test Database Connection
```bash
# Test from backend
cd backend
python -c "
from supabase import create_client
client = create_client('YOUR_URL', 'YOUR_KEY')
result = client.table('sensor_data').select('*').limit(1).execute()
print('Database connected:', result.data is not None)
"
```

---

## 🖥️ BACKEND DEPLOYMENT (RENDER)

### Step 1: Prepare Backend Code
1. Ensure `backend/production_backend.py` is ready
2. Ensure `backend/production_websocket.py` is ready
3. Update `backend/requirements.txt` with all dependencies

### Step 2: Deploy to Render
1. Connect GitHub repository to Render
2. Create **Web Service** for Backend API:
   - **Name**: `smart-agriculture-backend`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && python production_backend.py`
   - **Plan**: Starter ($7/month)

3. Create **Web Service** for WebSocket:
   - **Name**: `smart-agriculture-websocket`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && python production_websocket.py`
   - **Plan**: Starter ($7/month)

4. Create **Background Worker** for Telegram Bot:
   - **Name**: `smart-agriculture-telegram`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `python telegram_bot_simple.py`
   - **Plan**: Starter ($7/month)

### Step 3: Configure Environment Variables in Render
For **Backend API Service**:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
OPENWEATHER_API_KEY=your-openweather-key
TELEGRAM_BOT_TOKEN=your-telegram-token
TELEGRAM_CHAT_ID=your-chat-id
ALLOWED_ORIGINS=https://smart-agriculture-dashboard.vercel.app
NODE_ENV=production
HOST=0.0.0.0
PORT=8000
```

For **WebSocket Service**:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
ALLOWED_ORIGINS=https://smart-agriculture-dashboard.vercel.app
NODE_ENV=production
WS_HOST=0.0.0.0
WS_PORT=8080
```

For **Telegram Bot Worker**:
```bash
TELEGRAM_BOT_TOKEN=your-telegram-token
TELEGRAM_CHAT_ID=your-chat-id
OPENWEATHER_API_KEY=your-openweather-key
VITE_WS_URL=wss://smart-agriculture-websocket.onrender.com/ws
VITE_API_BASE_URL=https://smart-agriculture-backend.onrender.com
WEATHER_CITY=Erode
```

### Step 4: Test Backend Deployment
```bash
# Test API health
curl https://smart-agriculture-backend.onrender.com/health

# Test WebSocket health
curl https://smart-agriculture-websocket.onrender.com/health

# Test API endpoints
curl https://smart-agriculture-backend.onrender.com/model-metrics
curl https://smart-agriculture-backend.onrender.com/weather
```

---

## 🌐 FRONTEND DEPLOYMENT (VERCEL)

### Step 1: Prepare Frontend Code
1. Ensure all environment variables are properly configured
2. Update `vite.config.ts` for production builds
3. Test build locally: `npm run build:prod`

### Step 2: Deploy to Vercel
1. Connect GitHub repository to Vercel
2. Import project with these settings:
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build:prod`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

### Step 3: Configure Environment Variables in Vercel
```bash
VITE_API_BASE_URL=https://smart-agriculture-backend.onrender.com
VITE_WS_URL=wss://smart-agriculture-websocket.onrender.com/ws
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
VITE_OPENWEATHER_API_KEY=your-openweather-key
VITE_N8N_WEBHOOK_URL=https://your-n8n-instance.app.n8n.cloud/webhook/your-id/chat
VITE_ADMIN_EMAIL=admin@smartfarm.com
VITE_ADMIN_PASSWORD=your-secure-password
NODE_ENV=production
REACT_APP_ENV=production
```

### Step 4: Configure Custom Domain (Optional)
1. Add custom domain in Vercel dashboard
2. Update DNS records as instructed
3. SSL certificate will be automatically provisioned

### Step 5: Test Frontend Deployment
1. Visit your Vercel URL
2. Test authentication flow
3. Verify dashboard loads without errors
4. Test WebSocket connection
5. Verify weather data loads
6. Test offline mode (when ESP32 not connected)

---

## 🤖 TELEGRAM BOT DEPLOYMENT

### Step 1: Create Telegram Bot
1. Message @BotFather on Telegram
2. Create new bot: `/newbot`
3. Set bot name and username
4. Save the bot token securely
5. Get your chat ID by messaging the bot and checking updates

### Step 2: Configure Bot Commands
Message @BotFather:
```
/setcommands
weather - Get current weather report for Erode
dashboard - View sensor data and system status
pump on - Turn irrigation pump ON
pump off - Turn irrigation pump OFF
help - Show all available commands
```

### Step 3: Test Bot Functionality
1. Send `/start` to your bot
2. Test weather command: `weather`
3. Test dashboard command: `dashboard`
4. Verify scheduled reports work (7 AM and 6 PM)

---

## 🔧 EXTERNAL INTEGRATIONS

### OpenWeather API
1. Sign up at [openweathermap.org](https://openweathermap.org)
2. Get free API key (1000 calls/day)
3. Test API: `curl "http://api.openweathermap.org/data/2.5/weather?q=Erode,IN&appid=YOUR_KEY"`

### n8n Automation (Optional)
1. Set up n8n instance
2. Create webhook for chatbot integration
3. Configure workflows for automation
4. Update `VITE_N8N_WEBHOOK_URL` environment variable

---

## 🔒 SECURITY CONFIGURATION

### 1. Environment Variables Security
- [ ] Never commit `.env` files to git
- [ ] Use different keys for development and production
- [ ] Rotate API keys regularly
- [ ] Use strong passwords for admin accounts

### 2. CORS Configuration
- [ ] Restrict CORS to specific domains in production
- [ ] Update `ALLOWED_ORIGINS` in backend services
- [ ] Test cross-origin requests work correctly

### 3. Database Security
- [ ] Enable Row Level Security (RLS) in Supabase
- [ ] Create proper RLS policies for data access
- [ ] Use service role key only in backend
- [ ] Use anon key only in frontend

### 4. SSL/TLS Configuration
- [ ] Ensure all URLs use HTTPS/WSS in production
- [ ] Verify SSL certificates are valid
- [ ] Test WebSocket connections over WSS

---

## 📊 MONITORING & MAINTENANCE

### Health Check Endpoints
- Backend API: `https://smart-agriculture-backend.onrender.com/health`
- WebSocket: `https://smart-agriculture-websocket.onrender.com/health`
- Frontend: Monitor via Vercel dashboard

### Logging
- Backend logs available in Render dashboard
- Frontend errors tracked via browser console
- Telegram bot logs in worker service

### Database Monitoring
- Monitor Supabase dashboard for:
  - Database size and usage
  - Query performance
  - Connection counts
  - Error rates

### Automated Backups
- Supabase automatically backs up database
- Export model artifacts regularly
- Monitor data retention policies

---

## 🚨 TROUBLESHOOTING

### Common Issues

**1. Frontend shows "Offline" when ESP32 is connected**
- Check WebSocket URL in environment variables
- Verify WebSocket service is running on Render
- Test WebSocket connection manually

**2. Weather data not loading**
- Verify OpenWeather API key is valid
- Check API rate limits (1000 calls/day for free tier)
- Test API endpoint manually

**3. Telegram bot not responding**
- Check bot token and chat ID
- Verify Render worker service is running
- Check bot logs for errors

**4. Database connection errors**
- Verify Supabase URL and keys
- Check database connection limits
- Monitor Supabase dashboard for issues

**5. CORS errors in browser**
- Update `ALLOWED_ORIGINS` in backend services
- Verify frontend domain is whitelisted
- Check browser network tab for specific errors

### Performance Optimization
- Enable Vercel Edge Functions for faster response
- Use Supabase connection pooling
- Implement caching for weather data
- Optimize WebSocket message frequency

---

## ✅ FINAL DEPLOYMENT CHECKLIST

### Pre-Launch
- [ ] All services deployed and running
- [ ] Environment variables configured
- [ ] Database schema applied
- [ ] SSL certificates active
- [ ] Health checks passing
- [ ] Error handling tested

### Testing
- [ ] Frontend loads on production URL
- [ ] Authentication works correctly
- [ ] Dashboard shows real-time data (when ESP32 connected)
- [ ] Dashboard shows "Offline" state (when ESP32 not connected)
- [ ] Weather data loads from API
- [ ] Telegram bot responds to commands
- [ ] WebSocket connections stable
- [ ] Database reads/writes working

### Post-Launch
- [ ] Monitor service health
- [ ] Check error logs
- [ ] Verify scheduled tasks (Telegram reports)
- [ ] Test ESP32 connectivity
- [ ] Monitor database usage
- [ ] Set up alerts for service downtime

---

## 📞 SUPPORT & MAINTENANCE

### Service URLs
- **Frontend**: https://smart-agriculture-dashboard.vercel.app
- **Backend API**: https://smart-agriculture-backend.onrender.com
- **WebSocket**: wss://smart-agriculture-websocket.onrender.com/ws
- **Database**: Supabase Dashboard
- **Monitoring**: Render Dashboard, Vercel Dashboard

### Regular Maintenance Tasks
- Weekly: Check service health and logs
- Monthly: Review database usage and performance
- Quarterly: Rotate API keys and passwords
- Annually: Review and update dependencies

### Scaling Considerations
- Upgrade Render plans for higher traffic
- Implement Redis caching for better performance
- Use CDN for static assets
- Consider database read replicas for high load

---

## 🎉 DEPLOYMENT COMPLETE!

Your Smart Agriculture Dashboard is now production-ready with:

✅ **Scalable Architecture**: Frontend on Vercel, Backend on Render, Database on Supabase  
✅ **Real-time Data**: WebSocket connections for live sensor updates  
✅ **External Integrations**: Weather API, Telegram Bot, n8n Automation  
✅ **Security**: Environment variables, HTTPS/WSS, database security  
✅ **Monitoring**: Health checks, logging, error handling  
✅ **Reliability**: Auto-scaling, backups, failover handling  

The system is now ready for production use with ESP32 devices and can handle real agricultural monitoring workloads.