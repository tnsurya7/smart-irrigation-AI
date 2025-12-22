# 🚀 Frontend Deployment Guide - Vercel

## 📋 **Pre-Deployment Setup**

### ✅ **Backend Status:**
- Backend URL: https://smart-agriculture-backend-my7c.onrender.com
- Health Check: ✅ PASSING
- Weather API: ✅ WORKING
- Ready for frontend connection

## 🔧 **Vercel Deployment Steps**

### **Step 1: Connect Repository**
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"New Project"**
3. Import from GitHub: `tnsurya7/smart-irrigation-AI`
4. Select **Root Directory**: `.` (project root)

### **Step 2: Configure Build Settings**
- **Framework Preset**: Vite
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

### **Step 3: Environment Variables**
Add these environment variables in Vercel:

```
VITE_API_BASE_URL=https://smart-agriculture-backend-my7c.onrender.com/api
VITE_WS_URL=wss://smart-agriculture-backend-my7c.onrender.com/ws
VITE_SUPABASE_URL=https://zkqhyojleofjngbfeses.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InprcWh5b2psZW9qZm5nYmZlc2VzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYxNTA5MzQsImV4cCI6MjA4MTcyNjkzNH0.NanYQOCS0kNyKVkS5yQxdCOOp5naP15meTp_lWKyQ0M
VITE_OPENWEATHER_API_KEY=59ade005948b4c8f58a100afc603f047
VITE_N8N_WEBHOOK_URL=https://suryan8nproject.app.n8n.cloud/webhook/ccd37962-6bb3-4c30-b859-d3b63b9c64e2/chat
VITE_ADMIN_EMAIL=admin@smartfarm.com
VITE_ADMIN_PASSWORD=admin123
NODE_ENV=production
```

### **Step 4: Deploy**
1. Click **"Deploy"**
2. Wait for build to complete (2-3 minutes)
3. Get your deployment URL (e.g., `https://smart-agriculture-dashboard.vercel.app`)

## 🔗 **Post-Deployment Configuration**

### **Update Backend CORS**
After getting your Vercel URL, update the backend's ALLOWED_ORIGINS:

1. Go to Render Dashboard → smart-agriculture-backend → Environment
2. Update `ALLOWED_ORIGINS` to include your Vercel URL:
   ```
   ALLOWED_ORIGINS=https://your-vercel-url.vercel.app
   ```

## ✅ **Expected Results**

### **Working Features:**
- ✅ Dashboard loads without ESP32
- ✅ Weather data from backend API
- ✅ Safe defaults for sensor readings
- ✅ Responsive design
- ✅ All components render properly

### **Expected Issues (Normal):**
- ⚠️ Model metrics may show errors (Supabase connection)
- ⚠️ WebSocket connection may fail (no WebSocket server yet)
- ⚠️ Real sensor data unavailable (ESP32 not connected)

## 🧪 **Testing Checklist**

After deployment, test these URLs:
- [ ] Main dashboard loads
- [ ] Weather panel shows data
- [ ] Sensor cards show safe defaults (0.0 values)
- [ ] No blocking error screens
- [ ] Mobile responsive design works

## 🎯 **Success Criteria**

✅ **Frontend deployed successfully**  
✅ **Dashboard accessible via HTTPS**  
✅ **Backend API connection working**  
✅ **No blocking errors**  
✅ **Ready for ESP32 integration**

---

**Your Smart Agriculture Dashboard will be production-ready after this deployment!** 🌱