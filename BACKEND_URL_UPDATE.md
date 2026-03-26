# Backend URL Update Guide

## New Backend URL
```
https://smart-agriculture-backend-x8qu.onrender.com
```

## ✅ Code Updates (Already Done)

The following files have been updated with the new backend URL:

1. **Frontend WebSocket** (`hooks/useSmartFarmData.ts`)
   - Updated default WebSocket URL to: `wss://smart-agriculture-backend-x8qu.onrender.com/ws`

2. **ChatBot Component** (`components/ChatBot.tsx`)
   - Updated API URL to: `https://smart-agriculture-backend-x8qu.onrender.com`

3. **Historical Trend Explorer** (`components/HistoricalTrendExplorer.tsx`)
   - Updated fallback API URL to: `https://smart-agriculture-backend-x8qu.onrender.com`

4. **Backend CORS Settings** (`backend/production_backend.py`)
   - Updated allowed origins
   - Updated trusted hosts

## 🔧 Vercel Environment Variables (YOU NEED TO UPDATE)

Go to your Vercel dashboard and update these environment variables:

### Required Updates:

1. **VITE_API_BASE_URL**
   ```
   https://smart-agriculture-backend-x8qu.onrender.com/api
   ```

2. **VITE_WS_URL**
   ```
   wss://smart-agriculture-backend-x8qu.onrender.com/ws
   ```

### Steps to Update Vercel Environment Variables:

1. Go to: https://vercel.com/dashboard
2. Select your project: `smart-agriculture-dashboard-2025`
3. Go to **Settings** → **Environment Variables**
4. Find and update:
   - `VITE_API_BASE_URL` → `https://smart-agriculture-backend-x8qu.onrender.com/api`
   - `VITE_WS_URL` → `wss://smart-agriculture-backend-x8qu.onrender.com/ws`
5. Click **Save**
6. Go to **Deployments** tab
7. Click **Redeploy** on the latest deployment

## 📡 ESP32 Update (If Using Direct WebSocket)

If your ESP32 connects directly to the backend (not via USB bridge), update the WebSocket host:

```cpp
const char* ws_host = "smart-agriculture-backend-x8qu.onrender.com";
const int ws_port = 443;
const char* ws_path = "/ws";
```

## 🔍 Verification

After updating and redeploying:

1. **Check Backend Health**:
   ```bash
   curl https://smart-agriculture-backend-x8qu.onrender.com/health
   ```
   Should return: `{"status":"ok"}`

2. **Check WebSocket**:
   - Open dashboard: https://smart-agriculture-dashboard-2025.vercel.app
   - Open browser console (F12)
   - Look for: `🚀 Connecting to WebSocket: wss://smart-agriculture-backend-x8qu.onrender.com/ws`
   - Should see: `🔌 WebSocket connection opened`

3. **Check ESP32 Connection**:
   - ESP32 should connect and send data
   - Backend logs should show: `Received sensor data from ESP32`
   - Dashboard should show: `🟢 Connected`

## 📝 Other Files (Optional Updates)

These files also reference the old URL but are not critical for production:

- `.github/workflows/keep-alive.yml` (GitHub Actions health check)
- `test_*.py` (Test scripts)
- `*.md` (Documentation files)
- `usb_esp32_bridge.js` (USB bridge script)

You can update these later if needed.

## ✅ Deployment Checklist

- [x] Update frontend code (hooks, components)
- [x] Update backend CORS settings
- [x] Commit and push changes to Git
- [ ] Update Vercel environment variables
- [ ] Redeploy Vercel frontend
- [ ] Update ESP32 code (if needed)
- [ ] Verify WebSocket connection
- [ ] Test manual pump control
- [ ] Test auto irrigation mode

## 🚀 Quick Deploy Commands

```bash
# Commit changes
git add .
git commit -m "Update backend URL to smart-agriculture-backend-x8qu.onrender.com"
git push origin main

# Backend will auto-deploy to Render
# Frontend will auto-deploy to Vercel (after env var update)
```

## 🆘 Troubleshooting

### Dashboard shows "Offline"
- Check Vercel environment variables are updated
- Verify backend is running: `curl https://smart-agriculture-backend-x8qu.onrender.com/health`
- Check browser console for WebSocket errors

### ESP32 not connecting
- Verify ESP32 code has correct WebSocket host
- Check ESP32 serial monitor for connection errors
- Ensure backend allows `file://` origin for ESP32

### CORS errors
- Backend CORS settings updated (already done)
- Clear browser cache
- Try incognito/private browsing mode

---

**New Backend URL**: `https://smart-agriculture-backend-x8qu.onrender.com`

**Status**: Code updated ✅ | Vercel env vars pending ⏳
