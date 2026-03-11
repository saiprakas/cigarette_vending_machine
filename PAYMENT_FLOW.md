# Payment to Dispensing Flow

## ✅ Complete Integration Overview

### 1. Payment Initiation (Frontend)
When customer clicks **"Pay Now"**:
- Frontend calls: `POST /create-order` with cart amount
- Backend creates Razorpay payment link
- Returns: `payment_link_id` and `payment_url`
- Frontend opens payment window and starts polling

### 2. Payment Processing (Customer)
- Customer scans QR or enters UPI ID in opened window
- Completes payment on Razorpay page
- Payment status changes to "paid" on Razorpay

### 3. Payment Detection (Frontend Polling)
- Frontend polls: `GET /check-payment/{payment_link_id}` every 3 seconds
- Backend checks Razorpay: `payment_link.status == 'paid'`
- When paid detected → Frontend calls `startDispensing()`

### 4. ✨ Dispensing Trigger (NEW Security Layer)
**Frontend → Backend**:
```javascript
POST /dispense
{
  "payment_link_id": "plink_xxx",  // ← Payment proof
  "items": [...],                   // ← What to dispense
  "esp32_ip": "192.168.1.100"      // ← Where to send
}
```

### 5. 🔐 Backend Verification & ESP32 Trigger
**Backend Process**:

**Step 1: Re-verify Payment**
- Backend fetches payment link from Razorpay again
- Confirms `status == 'paid'` before dispensing
- ❌ If not paid → Return error, no dispense
- ✅ If paid → Proceed to Step 2

**Step 2: Send to ESP32**
```python
POST http://{esp32_ip}/dispense
{
  "items": [
    {"id": 1, "name": "Marlboro", "quantity": 2},
    {"id": 2, "name": "Gold Flake", "quantity": 1}
  ]
}
```

**Step 3: Handle Response**
- ✅ ESP32 Online → Real dispensing + Return success
- ⚠️ ESP32 Offline → Simulate dispense for demo (logs warning)
- ❌ ESP32 Error → Return error to frontend

### 6. Completion (Frontend)
- Shows "Dispensing..." animation
- Displays completion message
- Returns to landing page after 3 seconds

---

## 🔒 Security Features

1. **Double Payment Verification**:
   - Frontend polls payment status
   - Backend re-verifies before ESP32 trigger
   - Prevents unauthorized dispensing

2. **Payment Link Tracking**:
   - Every dispense request must include valid `payment_link_id`
   - Backend validates with Razorpay before action

3. **Error Handling**:
   - Payment not confirmed → No dispense
   - ESP32 offline → Logged, no crash
   - Network errors → Proper error messages

---

## 🧪 Testing the Flow

### Test 1: Payment Link Creation
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/create-order" -Method Post -Body '{"amount": 10}' -ContentType "application/json"
```
**Expected**: Returns `payment_link_id` and `payment_url`

### Test 2: Check Payment Status  
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/check-payment/plink_xxx" -Method Get
```
**Expected**: Returns `{"paid": false}` (until payment completed)

### Test 3: Dispense Trigger (Requires Paid Status)
```powershell
$body = @{
    payment_link_id = "plink_xxx"
    items = @(
        @{id=1; name="Test"; quantity=2}
    )
    esp32_ip = "192.168.1.100"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/dispense" -Method Post -Body $body -ContentType "application/json"
```
**Expected**: 
- If payment not paid → Error: "Payment not confirmed"
- If payment paid → Success: Dispenses items

---

## 📡 ESP32 Integration

Your ESP32 should expose endpoint:

**POST** `http://192.168.1.100/dispense`

**Request Body**:
```json
{
  "items": [
    {"id": 1, "name": "Marlboro", "quantity": 2},
    {"id": 2, "name": "Gold Flake", "quantity": 1}
  ]
}
```

**Response** (Expected):
```json
{
  "success": true,
  "message": "Dispensed 3 cigarettes"
}
```

---

## 🚀 Live Mode Checklist

When switching to live Razorpay:

1. ✅ Update credentials in `backend/app_simple.py`:
   ```python
   RAZORPAY_KEY_ID = "rzp_live_XXXXX"
   RAZORPAY_KEY_SECRET = "XXXXX"
   ```

2. ✅ Update credentials in `src/config.js`:
   ```javascript
   RAZORPAY_KEY_ID: 'rzp_live_XXXXX'
   ```

3. ✅ Test with small amount first (₹1)

4. ✅ Verify ESP32 connection

5. ✅ Monitor backend logs for payment confirmations

---

## 📋 Files Modified

- ✅ `backend/app_simple.py` - Added payment verification in `/dispense`
- ✅ `src/PaymentPage.jsx` - Added `payment_link_id` to dispense request
- ✅ `backend/app_simple.py` - Added `requests` library import

---

## 🎯 Current Status

**✅ Payment Creation**: Working  
**✅ Payment Detection**: Working (polling)  
**✅ Payment Verification**: Working (double-check)  
**✅ ESP32 Trigger**: Implemented (with fallback)  
**⏳ Live Mode**: Pending credentials  
**⏳ ESP32 Hardware**: Pending connection test

---

**Next Step**: Provide live Razorpay credentials to switch from test to production mode! 🚀
