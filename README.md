# Cigarette Vending Machine

An automated cigarette vending machine interface with age verification and smart dispensing system.

## Features

- 🎨 Modern UI with gradient theme (purple/orange)
- 👤 Age verification using camera
- 🛒 Shopping cart functionality
- 💳 Payment processing
- 🔧 Real-time dispensing console with solenoid tracking
- 📦 ESP32 integration for hardware control
- ✅ Thank you page with auto-redirect

## Quick Start

### Option 1: One-Click Start (Recommended)

**Double-click** the `START.bat` file in the project folder. This will automatically:
- Start the backend server (Port 5000)
- Start the frontend server (Port 5173)
- Open the application in your browser

### Option 2: Using NPM

```bash
npm start
```

### Option 3: Using PowerShell

```powershell
.\start.ps1
```

### Option 4: Manual Start (Advanced)

If you need to run servers separately:

**Terminal 1 - Backend:**
```bash
cd backend
python app_simple.py
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

## Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000

## Tech Stack

### Frontend
- React 19.2.0
- Vite 7.3.1
- Modern CSS with gradients and animations

### Backend
- Python Flask
- Age verification (demo mode)
- ESP32 dispenser integration

## Color Scheme

- Background: Purple gradient (#1a1c2e to #2d1b3d)
- Primary Buttons: Teal (#008080, #17a2b8)
- Accents: Orange (#F7931E)
- Text: White (#FFFFFF)

## Project Structure

```
├── src/                    # Frontend React components
│   ├── App.jsx            # Main app with routing
│   ├── Products.jsx       # Product selection page
│   ├── Cart.jsx           # Cart component
│   ├── CartPage.jsx       # Cart page view
│   ├── PaymentPage.jsx    # Payment & dispensing
│   └── AgeVerification.jsx # Age verification modal
├── backend/               # Flask backend
│   ├── app_simple.py      # Demo mode server
│   └── app.py             # Full server with DeepFace
├── esp32/                 # ESP32 Arduino code
└── START.bat              # One-click launcher

```

## Development

### Prerequisites
- Node.js and npm
- Python 3.8+
- Virtual environment (`.venv`)

### Installing Dependencies

**Frontend:**
```bash
npm install
```

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

## Hardware Integration

The system communicates with ESP32 via HTTP to control solenoid valves for cigarette dispensing. See `ESP32_SETUP.md` for hardware configuration.

## Demo Mode

The application runs in demo mode by default (using `app_simple.py`), which:
- Simulates age verification without requiring a camera
- Returns random ages between 22-32
- Always approves access for testing

## License

Private project - All rights reserved

---

**Need Help?** Check the additional documentation:
- `ESP32_SETUP.md` - Hardware setup guide
- `AGE_VERIFICATION_SETUP.md` - Camera setup for production
- `TESTING_WITHOUT_HARDWARE.md` - Software testing guide
