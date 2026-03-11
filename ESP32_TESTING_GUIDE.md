# ESP32 Testing Without Physical Hardware

## How to Test Serial Monitor Output

### Step 1: Upload Code to ESP32
1. Open `esp32/cigarette_dispenser.ino` in Arduino IDE
2. Update WiFi credentials:
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   ```
3. Upload to ESP32

### Step 2: Open Serial Monitor
1. In Arduino IDE, click **Tools → Serial Monitor** (or press Ctrl+Shift+M)
2. Set baud rate to **115200** (bottom right corner)
3. You should see:
   ```
   === Cigarette Vending Machine ESP32 ===
   Connecting to WiFi: YourWiFiName
   WiFi Connected!
   IP Address: 192.168.1.100
   HTTP server started
   ```

### Step 3: Note Your ESP32 IP Address
Look for the line: `IP Address: 192.168.1.100`
This is your ESP32's IP - you'll need it for testing!

### Step 4: Test from Command Line or Postman

#### Option A: Using PowerShell (Windows)
```powershell
# Test 1: Single solenoid
Invoke-RestMethod -Uri "http://192.168.1.100/test" -Method POST -ContentType "application/json" -Body '{"solenoid_id": 1}'

# Test 2: Multiple pushes (2x Cigarette 1)
Invoke-RestMethod -Uri "http://192.168.1.100/dispense" -Method POST -ContentType "application/json" -Body '{"items": [{"id": 1, "quantity": 2}]}'

# Test 3: Multiple cigarettes (2x Cigarette 1, 3x Cigarette 2)
Invoke-RestMethod -Uri "http://192.168.1.100/dispense" -Method POST -ContentType "application/json" -Body '{"items": [{"id": 1, "quantity": 2}, {"id": 2, "quantity": 3}]}'
```

#### Option B: Using curl (Linux/Mac/Git Bash)
```bash
# Test 1: Single solenoid
curl -X POST http://192.168.1.100/test \
  -H "Content-Type: application/json" \
  -d '{"solenoid_id": 1}'

# Test 2: Multiple pushes (2x Cigarette 1)
curl -X POST http://192.168.1.100/dispense \
  -H "Content-Type: application/json" \
  -d '{"items": [{"id": 1, "quantity": 2}]}'

# Test 3: Multiple cigarettes (2x Cigarette 1, 3x Cigarette 2)
curl -X POST http://192.168.1.100/dispense \
  -H "Content-Type: application/json" \
  -d '{"items": [{"id": 1, "quantity": 2}, {"id": 2, "quantity": 3}]}'
```

#### Option C: Using Web Browser
Open your browser and go to: `http://192.168.1.100`
You'll see a web interface with example commands!

## What You'll See in Serial Monitor

### Example: Order 2x Cigarette 1

When you send the dispense command, the Serial Monitor will show:

```
Dispense request received:
{"items":[{"id":1,"quantity":2}]}

╔════════════════════════════════════════╗
║   STARTING SEQUENTIAL DISPENSING       ║
╚════════════════════════════════════════╝

┌────────────────────────────────────┐
│ Cigarette 1 - Quantity: 2           │
└────────────────────────────────────┘

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

╔════════════════════════════════════════╗
║     DISPENSING COMPLETE! ✅             ║
╚════════════════════════════════════════╝
🎯 Total cigarettes dispensed: 2
```

### Example: Order 2x Cigarette 1, 3x Cigarette 2

```
╔════════════════════════════════════════╗
║   STARTING SEQUENTIAL DISPENSING       ║
╚════════════════════════════════════════╝

┌────────────────────────────────────┐
│ Cigarette 1 - Quantity: 2           │
└────────────────────────────────────┘

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

⏳ Waiting 1000ms before next push...

┌────────────────────────────────────┐
│ Cigarette 2 - Quantity: 3           │
└────────────────────────────────────┘

====================================
🚬 PUSHING SOLENOID 2 (Cigarette 2)
====================================
📍 Push Number: 1 of 3
🔌 GPIO Pin: 4
⚡ Activating Relay → Solenoid 2 ON
⏱️  Pushing for 500ms...
✅ Solenoid 2 PUSHED - Relay OFF
====================================

⏳ Waiting 1000ms before next push...

====================================
🚬 PUSHING SOLENOID 2 (Cigarette 2)
====================================
📍 Push Number: 2 of 3
🔌 GPIO Pin: 4
⚡ Activating Relay → Solenoid 2 ON
⏱️  Pushing for 500ms...
✅ Solenoid 2 PUSHED - Relay OFF
====================================

⏳ Waiting 1000ms before next push...

====================================
🚬 PUSHING SOLENOID 2 (Cigarette 2)
====================================
📍 Push Number: 3 of 3
🔌 GPIO Pin: 4
⚡ Activating Relay → Solenoid 2 ON
⏱️  Pushing for 500ms...
✅ Solenoid 2 PUSHED - Relay OFF
====================================

╔════════════════════════════════════════╗
║     DISPENSING COMPLETE! ✅             ║
╚════════════════════════════════════════╝
🎯 Total cigarettes dispensed: 5
```

## Key Information in Output

Each push shows you:
- 🚬 **Which solenoid** is being activated (1-16)
- 📍 **Push number** (e.g., "1 of 2" means first push out of 2 total)
- 🔌 **GPIO pin** being used (for hardware wiring reference)
- ⚡ **Activation status** (when relay turns ON)
- ⏱️ **Duration** (how long the push lasts)
- ✅ **Completion** (when relay turns OFF)
- ⏳ **Wait time** between pushes

## Testing Full System (Frontend → Backend → ESP32)

1. **Start Backend** (if not already running):
   ```powershell
   cd backend
   C:\venv_ai\Scripts\python.exe app.py
   ```

2. **Start Frontend** (if not already running):
   ```powershell
   npm run dev
   ```

3. **Open Frontend**: http://localhost:5173

4. **Test Complete Flow**:
   - Add cigarettes to cart
   - Proceed to checkout
   - Complete age verification
   - Enter ESP32 IP address (e.g., `192.168.1.100`)
   - Click "Pay Now"
   - Watch Serial Monitor for dispensing!

## Troubleshooting

### Nothing in Serial Monitor?
- Check baud rate is set to 115200
- Press EN/RST button on ESP32 to restart
- Verify USB cable is connected

### ESP32 Not Responding to Commands?
- Check ESP32 IP address in Serial Monitor
- Ping ESP32: `ping 192.168.1.100`
- Open browser: `http://192.168.1.100`
- Check firewall settings

### Want More/Less Detail?
Edit `cigarette_dispenser.ino` and adjust the Serial.println messages in the `activateSolenoid()` function.

## GPIO Pin Reference

```
Cigarette ID → GPIO Pin → Solenoid
------------------------------------
1  → GPIO 2   → Solenoid 1
2  → GPIO 4   → Solenoid 2
3  → GPIO 5   → Solenoid 3
4  → GPIO 12  → Solenoid 4
5  → GPIO 13  → Solenoid 5
6  → GPIO 14  → Solenoid 6
7  → GPIO 15  → Solenoid 7
8  → GPIO 16  → Solenoid 8
9  → GPIO 17  → Solenoid 9
10 → GPIO 18  → Solenoid 10
11 → GPIO 19  → Solenoid 11
12 → GPIO 21  → Solenoid 12
13 → GPIO 22  → Solenoid 13
14 → GPIO 23  → Solenoid 14
15 → GPIO 25  → Solenoid 15
16 → GPIO 26  → Solenoid 16
```

## Notes

- **Without physical relays/solenoids**: You'll see the messages but nothing will physically push. The built-in LED on GPIO 2 will blink during Cigarette 1 pushes!
  
- **With physical hardware**: You'll see the messages AND hear/see the relays clicking and solenoids pushing.

- **Timing**: Each push takes 500ms, with 1 second delay between pushes. Total time = (number of cigarettes × 1.5 seconds).

- **LED Indicator**: The built-in LED (usually on GPIO 2) will light up during each push, giving you visual feedback even without hardware connected!

---

**Ready to test!** Upload the code, open Serial Monitor, and send commands to see detailed output! 🎯
