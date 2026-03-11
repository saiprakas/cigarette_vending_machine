# Quick Start: Testing ESP32 Without Hardware

## What You'll See (Without Physical Hardware)

When you test the ESP32 solenoid controller **without physical relays/solenoids connected**, you will see **detailed output messages in the Serial Monitor** that show exactly what would be happening if hardware was connected.

## Example Output

### If you order 2 cigarettes from Cigarette 1:

```
====================================
🚬 PUSHING SOLENOID 1 (Cigarette 1)
====================================
📍 Push Number: 1 of 2
🔌 GPIO Pin: 2
⚡ Activating Relay → Solenoid 1 ON
⏱️  Pushing for 500ms...
✅ Solenoid 1 PUSHED - Relay OFF
====================================

⏳ Waiting 1000ms before next push...

====================================
🚬 PUSHING SOLENOID 1 (Cigarette 1)
====================================
📍 Push Number: 2 of 2
🔌 GPIO Pin: 2
⚡ Activating Relay → Solenoid 1 ON
⏱️  Pushing for 500ms...
✅ Solenoid 1 PUSHED - Relay OFF
====================================
```

## Quick Testing Steps

### 1. Upload Code to ESP32
1. Open `esp32/cigarette_dispenser.ino` in Arduino IDE
2. Edit WiFi credentials (lines 8-9):
   ```cpp
   const char* ssid = "YOUR_WIFI_NAME";
   const char* password = "YOUR_WIFI_PASSWORD";
   ```
3. Click Upload (→ button)

### 2. Open Serial Monitor
1. Click **Tools → Serial Monitor** (or Ctrl+Shift+M)
2. Set baud rate to **115200** (bottom right)
3. Look for: `IP Address: 192.168.1.XXX` ← Note this IP!

### 3. Run Test Script (Easy Way)
```powershell
# In PowerShell
cd C:\Users\hp\OneDrive\Desktop\Ciggrete_vending_machine
.\test_esp32.ps1
```

Or test manually:
```powershell
# Replace 192.168.1.100 with your ESP32 IP
Invoke-RestMethod -Uri "http://192.168.1.100/dispense" -Method POST -ContentType "application/json" -Body '{"items": [{"id": 1, "quantity": 2}]}'
```

### 4. Watch Serial Monitor
You'll see detailed messages showing each solenoid push!

## Files Created

1. **esp32/cigarette_dispenser.ino** - Enhanced with detailed Serial output
2. **test_esp32.ps1** - PowerShell script for easy testing
3. **ESP32_TESTING_GUIDE.md** - Detailed testing documentation
4. **ESP32_SETUP.md** - Full hardware setup guide

## What Each Message Means

- **🚬 PUSHING SOLENOID X** - Which cigarette slot is being activated
- **📍 Push Number: 1 of 2** - This is push #1 out of 2 total pushes needed
- **🔌 GPIO Pin: 2** - Which ESP32 pin is being used (for wiring reference)
- **⚡ Activating Relay** - The relay would turn ON now (solenoid pushes)
- **⏱️ Pushing for 500ms** - How long the push lasts
- **✅ PUSHED - Relay OFF** - Push complete, relay would turn OFF
- **⏳ Waiting 1000ms** - Delay before next push

## Bonus: Built-in LED
If you're testing **Cigarette 1** (Solenoid 1, GPIO 2), you might see the built-in LED on the ESP32 blinking during pushes! This gives you visual feedback even without hardware.

## Next Steps

Once you verify the serial output is working correctly:
1. Connect your relay module
2. Connect solenoids to relays
3. Test with actual hardware!

See **ESP32_SETUP.md** for full hardware wiring guide.

---

**Quick Test Command:**
```powershell
# Test 2 pushes of same solenoid (best for "pushed solenoid 1, pushed solenoid 1" demo)
Invoke-RestMethod -Uri "http://ESP32_IP/dispense" -Method POST -ContentType "application/json" -Body '{"items": [{"id": 1, "quantity": 2}]}'
```

Replace `ESP32_IP` with your actual IP address! 🚀
