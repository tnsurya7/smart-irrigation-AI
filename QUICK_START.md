# 🚀 QUICK START GUIDE

## Smart Agriculture Dashboard - Ready to Use!

---

## ⚡ Start the System

### 1. Start Backend (Terminal 1)
```bash
source venv/bin/activate
python fastapi_arimax_autoretrain.py
```
✅ Backend running at: http://localhost:8000

### 2. Start Frontend (Terminal 2)
```bash
npm run dev
```
✅ Dashboard running at: http://localhost:3000

---

## 🔌 Connect ESP32

### Update WebSocket URL
Edit `hooks/useSmartFarmData.ts`:
```typescript
const WS_URL = "ws://YOUR_ESP32_IP:8080";
```

### ESP32 Should Send
```json
{
  "type": "sensors",
  "soil": 1234,
  "rain": 0,
  "light": 300,
  "temperature": 26.1,
  "humidity": 61.2,
  "flow": 0.0,
  "totalLiters": 1.23,
  "pump": 0
}
```

### ESP32 Will Receive
```json
{
  "type": "cmd",
  "cmd": "pump",
  "value": "ON"
}
```

---

## 📱 Install as PWA

### iOS
1. Open in Safari
2. Tap Share → Add to Home Screen

### Android
1. Open in Chrome
2. Tap Menu → Install app

### Desktop
1. Open in Chrome
2. Click install icon in address bar

---

## 🎯 Features

✅ Real-time sensor monitoring  
✅ Auto irrigation (3 rules)  
✅ Manual pump control  
✅ ML predictions (ARIMAX)  
✅ Historical charts  
✅ PWA installable  
✅ Offline support  

---

## 🔧 Configuration

### Change Cooldown Time
`hooks/useSmartFarmData.ts` line 56:
```typescript
setTimeout(() => setCooldown(false), 8000); // 8 seconds
```

### Change Pulse Duration
`hooks/useSmartFarmData.ts` line 66:
```typescript
setTimeout(() => sendPump("OFF"), 3000); // 3 seconds
```

### Change Auto-Retrain Interval
`fastapi_arimax_autoretrain.py` line 35:
```python
RETRAIN_INTERVAL_SECONDS = 24 * 60 * 60  # 24 hours
```

---

## 📊 Current Status

**Backend:** ✅ Running (Port 8000)  
**Frontend:** ✅ Running (Port 3000)  
**Models:** ✅ Trained (600 samples)  
**Best Model:** ✅ ARIMAX  
**WebSocket:** ✅ Ready  
**PWA:** ✅ Configured  
**TypeScript:** ✅ No errors  

---

## 🆘 Troubleshooting

### Backend not starting?
```bash
pip install -r requirements.txt
```

### Frontend not starting?
```bash
npm install
```

### WebSocket not connecting?
- Check ESP32 IP address
- Ensure ESP32 is on same network
- Check firewall settings

### PWA not installing?
- Create icon-192.png and icon-512.png
- See public/icon-info.txt

---

## 📖 Full Documentation

See `COMPLETE_SYSTEM_READY.md` for comprehensive documentation.

---

**Ready to farm smart! 🌱**
