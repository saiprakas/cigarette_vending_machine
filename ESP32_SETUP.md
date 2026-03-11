# ESP32 Cigarette Dispenser Setup Guide

## Hardware Requirements

### Components Needed:
1. **ESP32 Development Board** (1x)
2. **16-Channel Relay Module** (1x) - 5V or 12V
3. **16 Solenoid Pushers** (12V recommended)
4. **Power Supply**:
   - 5V 2A for ESP32
   - 12V 5A+ for solenoids (depending on solenoid current)
5. **Connecting Wires**
6. **Breadboard** (optional, for testing)

## Wiring Diagram

### ESP32 to Relay Module:
```
ESP32 GPIO → Relay Module Input
---------------------------------
GPIO 2    → Relay 1  (Cigarette 1)
GPIO 4    → Relay 2  (Cigarette 2)
GPIO 5    → Relay 3  (Cigarette 3)
GPIO 12   → Relay 4  (Cigarette 4)
GPIO 13   → Relay 5  (Cigarette 5)
GPIO 14   → Relay 6  (Cigarette 6)
GPIO 15   → Relay 7  (Cigarette 7)
GPIO 16   → Relay 8  (Cigarette 8)
GPIO 17   → Relay 9  (Cigarette 9)
GPIO 18   → Relay 10 (Cigarette 10)
GPIO 19   → Relay 11 (Cigarette 11)
GPIO 21   → Relay 12 (Cigarette 12)
GPIO 22   → Relay 13 (Cigarette 13)
GPIO 23   → Relay 14 (Cigarette 14)
GPIO 25   → Relay 15 (Cigarette 15)
GPIO 26   → Relay 16 (Cigarette 16)

ESP32 GND → Relay GND
ESP32 5V  → Relay VCC (if 5V relay module)
```

### Relay Module to Solenoids:
```
Relay COM (Common)  → 12V Power Supply (+)
Relay NO (Normally Open) → Solenoid (+)
Solenoid (-) → Power Supply Ground (-)
```

**IMPORTANT**: 
- Each relay controls ONE solenoid
- Use diodes (1N4007) across solenoid terminals to protect against back EMF
- Ensure proper power supply capacity for all solenoids

## Software Setup

### 1. Install Arduino IDE
Download from: https://www.arduino.cc/en/software

### 2. Install ESP32 Board Support
1. Open Arduino IDE
2. Go to **File → Preferences**
3. Add this URL to "Additional Board Manager URLs":
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Go to **Tools → Board → Boards Manager**
5. Search for "ESP32" and install **esp32 by Espressif Systems**

### 3. Install Required Libraries
1. Go to **Sketch → Include Library → Manage Libraries**
2. Search and install:
   - **ArduinoJson** (by Benoit Blanchon)

### 4. Upload Code to ESP32
1. Open `esp32/cigarette_dispenser.ino` in Arduino IDE
2. **IMPORTANT**: Edit WiFi credentials:
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";        // Your WiFi name
   const char* password = "YOUR_WIFI_PASSWORD"; // Your WiFi password
   ```
3. Select your ESP32 board:
   - **Tools → Board → ESP32 Arduino → ESP32 Dev Module**
4. Select the correct port:
   - **Tools → Port → COM3** (Windows) or **/dev/ttyUSB0** (Linux)
5. Click **Upload** button (→)

### 5. Find ESP32 IP Address
1. Open **Serial Monitor** (Ctrl+Shift+M or Tools → Serial Monitor)
2. Set baud rate to **115200**
3. Press **EN/RST** button on ESP32
4. Look for output:
   ```
   WiFi Connected!
   IP Address: 192.168.1.100
   ```
5. **Note this IP address** - you'll need it!

## Backend Configuration

### Update ESP32 IP in Frontend:
When you reach the payment page, you'll see an input field to enter the ESP32 IP address. Enter the IP you noted from the Serial Monitor (e.g., `192.168.1.100`).

Alternatively, you can set a default IP in the code:
1. Open `src/PaymentPage.jsx`
2. Find this line:
   ```javascript
   const [esp32Ip, setEsp32Ip] = useState('192.168.1.100')
   ```
3. Change `192.168.1.100` to your ESP32's actual IP

You can also set it in the backend:
1. Open `backend/app.py`
2. Find this line in `/dispense` endpoint:
   ```python
   esp32_ip = data.get('esp32_ip', '192.168.1.100')
   ```
3. Change the default IP

## Testing

### 1. Test ESP32 Alone
Open Serial Monitor and watch for:
```
=== Cigarette Vending Machine ESP32 ===
Connecting to WiFi: YourWiFiName
WiFi Connected!
IP Address: 192.168.1.100
HTTP server started
```

### 2. Test from Browser
Open browser and go to: `http://192.168.1.100` (use your ESP32 IP)

You should see:
```
Cigarette Vending Machine
ESP32 Dispenser Controller
Status: Online
```

### 3. Test Single Solenoid
Using a tool like Postman or curl:
```bash
curl -X POST http://192.168.1.100/test \
  -H "Content-Type: application/json" \
  -d '{"solenoid_id": 1}'
```

This will activate Solenoid 1 for 0.5 seconds.

### 4. Test Full System
1. Start the vending machine frontend
2. Add cigarettes to cart
3. Go to payment page
4. Enter ESP32 IP address
5. Click "Pay Now"
6. Watch solenoids activate sequentially!

## How It Works

### Sequential Dispensing:
If you order:
- Cigarette 1: Quantity 2
- Cigarette 2: Quantity 3

The ESP32 will:
1. Activate Solenoid 1 (push) → Wait 1 second
2. Activate Solenoid 1 (push) → Wait 1 second
3. Activate Solenoid 2 (push) → Wait 1 second
4. Activate Solenoid 2 (push) → Wait 1 second
5. Activate Solenoid 2 (push) → Done!

Each solenoid push lasts **500ms** (0.5 seconds).
Between pushes, there's a **1 second delay**.

### API Endpoints:

#### Check Status:
```
GET http://192.168.1.100/status
Response: {"status":"online","ip":"192.168.1.100","solenoids":16}
```

#### Dispense Cigarettes:
```
POST http://192.168.1.100/dispense
Content-Type: application/json

{
  "items": [
    {"id": 1, "quantity": 2},
    {"id": 3, "quantity": 1}
  ]
}

Response: {
  "success": true,
  "dispensed": 3,
  "message": "Dispensing complete"
}
```

## Troubleshooting

### ESP32 Not Connecting to WiFi:
- Check WiFi credentials in code
- Ensure 2.4GHz WiFi (ESP32 doesn't support 5GHz)
- Check WiFi signal strength
- Restart ESP32 (press EN/RST button)

### Relays Not Activating:
- Check wiring (GPIO pins to relay inputs)
- Ensure relay module has power (VCC and GND)
- Test with built-in LED (GPIO 2) - it should blink during pushes
- Check relay type: Active HIGH or Active LOW

### Backend Cannot Reach ESP32:
- Ensure ESP32 and computer are on same network
- Check ESP32 IP in Serial Monitor
- Ping ESP32: `ping 192.168.1.100`
- Check firewall settings
- Try accessing `http://ESP32_IP` in browser

### Solenoids Not Pushing:
- Check solenoid power supply (12V, sufficient current)
- Verify relay connections (COM → +12V, NO → Solenoid)
- Add flyback diodes across solenoids
- Test solenoid directly with power supply
- Check push duration (increase if needed)

## Adjusting Parameters

### Push Duration:
In `cigarette_dispenser.ino`:
```cpp
const int PUSH_DURATION = 500;  // Change to 800 for longer push
```

### Delay Between Pushes:
```cpp
const int DELAY_BETWEEN_PUSHES = 1000;  // Change to 1500 for more delay
```

### Change GPIO Pins:
```cpp
const int SOLENOID_PINS[16] = {
  2, 4, 5, 12, 13, 14, 15, 16,  // First 8
  17, 18, 19, 21, 22, 23, 25, 26 // Last 8
};
```

## Safety Notes

⚠️ **Important Safety Information:**
1. **Never hot-plug** solenoids while powered
2. **Always use flyback diodes** (1N4007 or equivalent)
3. **Proper power supply** - calculate total current needed
4. **Heat management** - solenoids and relays can get hot
5. **Secure mounting** - vibrations can loosen connections
6. **Emergency stop** - consider adding an emergency cutoff switch

## System Architecture

```
[User Browser]
    ↓ (Add items, checkout)
[React Frontend] (localhost:5173)
    ↓ (Age verification)
[Flask Backend] (localhost:5000)
    ↓ (Payment complete)
[Backend /dispense endpoint]
    ↓ (HTTP POST with order)
[ESP32] (192.168.1.x)
    ↓ (Sequential activation)
[16-Channel Relay Module]
    ↓ (Power switching)
[16 Solenoid Pushers]
    ↓ (Physical push)
[Cigarette Dispensing!] 🚬
```

## Support

For issues or questions:
1. Check Serial Monitor for ESP32 debug messages
2. Check browser console (F12) for frontend errors
3. Check backend terminal for Python errors
4. Verify all connections with multimeter
5. Test each component individually

---

**Created for Cigarette Vending Machine Project**
**March 2026**
