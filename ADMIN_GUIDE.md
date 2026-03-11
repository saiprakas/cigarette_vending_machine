# ADMIN GUIDE - CONFIDENTIAL

## Admin Access and Configuration

This guide contains sensitive information for system administrators only. **DO NOT share with customers.**

---

## Configuration File

**Location:** `src/config.js`

### Sensitive Settings:

```javascript
ESP32_IP: '192.168.1.100'  // Hardware dispenser IP address
BACKEND_URL: 'http://localhost:5000'  // Backend API URL
SHOW_CONSOLE_LOGS: false  // Set to true to see technical dispensing logs
```

### Enabling Admin Mode:

To see technical details and dispensing console:

1. Open `src/config.js`
2. Change `SHOW_CONSOLE_LOGS: false` to `SHOW_CONSOLE_LOGS: true`
3. Save and refresh the application

**IMPORTANT:** Always set back to `false` for customer use!

---

## ESP32 Hardware Configuration

**IP Address:** Set in `src/config.js` as `ESP32_IP`

**Default:** `192.168.1.100`

**To Change:**
- Edit `ESP32_IP` value in `src/config.js`
- Restart the application

---

## Backend Server

**File:** `backend/app_simple.py` (Demo mode)

**Port:** 5000

**Endpoints:**
- `/verify-age` - Age verification (POST with base64 image)
- `/dispense` - Cigarette dispensing (POST with items array)

### Backend Configuration:

The backend runs in demo mode by default:
- Always approves age verification
- Returns random age between 22-32
- Simulates successful dispensing

---

## Customer-Facing Security

### What Customers See:
✅ Simple payment interface
✅ Basic status messages ("Processing...", "Dispensing...")
✅ Clean error messages (no technical details)
✅ Thank you screen

### What Customers DON'T See:
❌ ESP32 IP address
❌ Backend API endpoints
❌ Solenoid numbers and technical logs
❌ System error details
❌ Configuration settings
❌ Console logs

---

## Security Best Practices

1. **Never expose `config.js` to customers**
2. **Keep backend logs private** - Check `SHOW_CONSOLE_LOGS` is false
3. **Protect backend API** - Use firewall rules in production
4. **Change default passwords** - Update `ADMIN_PASSWORD` in config
5. **Regular updates** - Keep dependencies updated
6. **Monitor logs** - Check backend logs for suspicious activity

---

## Troubleshooting (Admin Only)

### Enable Technical Console:
```javascript
// src/config.js
SHOW_CONSOLE_LOGS: true
```

### Check Backend Connection:
```bash
curl http://localhost:5000/
```

### View Dispensing Logs:
Enable console logs and check browser console (F12)

### Test ESP32 Connection:
```bash
curl http://192.168.1.100/status
```

---

## Emergency Procedures

### System Not Dispensing:
1. Check backend is running (port 5000)
2. Verify ESP32 IP address in config.js
3. Test ESP32 connection manually
4. Check dispensing console (enable logs)

### Age Verification Failing:
1. Restart backend server
2. Check camera permissions
3. Verify backend endpoint responding

### Customer Complaints:
1. Check error logs in backend
2. Review recent transactions
3. Test dispensing manually

---

## Production Deployment

Before deploying to production:

- [ ] Set `SHOW_CONSOLE_LOGS: false`
- [ ] Change `ADMIN_PASSWORD`
- [ ] Configure real ESP32 IP address
- [ ] Test age verification with real camera
- [ ] Set up backend with proper security
- [ ] Configure HTTPS for API
- [ ] Set up logging and monitoring
- [ ] Create backup procedures

---

**This document is CONFIDENTIAL - Admin access only**
