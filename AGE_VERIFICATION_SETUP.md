# Age Verification System - Setup Guide

## Overview
This cigarette vending machine includes a camera-based age verification system that captures the user's face and verifies their age before allowing purchase.

## Current Status
The frontend interface is **fully implemented** with:
- Camera access and video capture
- Face detection UI guide
- Real-time scanning animations
- Success/failure feedback
- Currently using **DEMO MODE** (simulates age detection)

## Backend Integration Required

### Python Backend for Age Detection

To enable **real age detection**, you need to set up a Python backend API that:
1. Receives the captured face image
2. Analyzes the face using ML/AI
3. Estimates the age
4. Returns the result

### Option 1: Using Face++ API (Easiest)

```python
# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import base64

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Get your API key from https://www.faceplusplus.com/
FACE_API_KEY = "your_face++_api_key"
FACE_API_SECRET = "your_face++_api_secret"

@app.route('/verify-age', methods=['POST'])
def verify_age():
    try:
        # Get uploaded image
        image_file = request.files['image']
        image_bytes = image_file.read()
        
        # Send to Face++ API
        url = "https://api-us.faceplusplus.com/facepp/v3/detect"
        files = {'image_file': image_bytes}
        data = {
            'api_key': FACE_API_KEY,
            'api_secret': FACE_API_SECRET,
            'return_attributes': 'age'
        }
        
        response = requests.post(url, data=data, files={'image_file': image_bytes})
        result = response.json()
        
        # Extract age
        if 'faces' in result and len(result['faces']) > 0:
            estimated_age = result['faces'][0]['attributes']['age']['value']
            
            return jsonify({
                'success': True,
                'estimated_age': estimated_age,
                'is_verified': estimated_age >= 19
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No face detected'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### Option 2: Using DeepFace (Local ML Model)

```python
# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from deepface import DeepFace
import cv2
import numpy as np
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

@app.route('/verify-age', methods=['POST'])
def verify_age():
    try:
        # Get uploaded image
        image_file = request.files['image']
        image = Image.open(io.BytesIO(image_file.read()))
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Analyze face
        analysis = DeepFace.analyze(
            img_path=img_array,
            actions=['age'],
            enforce_detection=True
        )
        
        estimated_age = analysis[0]['age']
        
        return jsonify({
            'success': True,
            'estimated_age': estimated_age,
            'is_verified': estimated_age >= 19
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### Installation Steps

1. **Install Python dependencies:**
```bash
pip install flask flask-cors requests
# For Face++ API
pip install requests

# For DeepFace (local ML)
pip install deepface opencv-python pillow
```

2. **Run the Python server:**
```bash
python backend/app.py
```

3. **Update Frontend API URL:**

In `src/AgeVerification.jsx`, uncomment and update the API call section (lines 48-56):

```javascript
// Replace the DEMO MODE section with:
const formData = new FormData()
formData.append('image', blob)

const response = await fetch('http://localhost:5000/verify-age', {
  method: 'POST',
  body: formData
})

const data = await response.json()

if (data.success) {
  const estimatedAge = data.estimated_age
  setDetectedAge(estimatedAge)
  
  if (estimatedAge >= 19) {
    setStatus('verified')
    setTimeout(() => {
      stopCamera()
      onVerified()
    }, 2000)
  } else {
    setStatus('failed')
    setErrorMessage(`Access Denied: Estimated age is ${estimatedAge}. Must be 19 or older.`)
  }
} else {
  throw new Error(data.error || 'Age verification failed')
}
```

### Option 3: Using Azure Face API

```python
# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
import io

app = Flask(__name__)
CORS(app)

# Get your keys from Azure Portal
FACE_KEY = "your_azure_face_key"
FACE_ENDPOINT = "your_azure_endpoint"

face_client = FaceClient(FACE_ENDPOINT, CognitiveServicesCredentials(FACE_KEY))

@app.route('/verify-age', methods=['POST'])
def verify_age():
    try:
        image_file = request.files['image']
        image_stream = io.BytesIO(image_file.read())
        
        # Detect faces with age attribute
        detected_faces = face_client.face.detect_with_stream(
            image=image_stream,
            return_face_attributes=['age']
        )
        
        if detected_faces:
            estimated_age = detected_faces[0].face_attributes.age
            
            return jsonify({
                'success': True,
                'estimated_age': int(estimated_age),
                'is_verified': estimated_age >= 19
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No face detected'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

## Testing

1. Start your Python backend
2. Start the React app: `npm run dev`
3. Add items to cart
4. Click "Proceed to Checkout"
5. Allow camera access
6. Position face in the oval guide
7. Click "Scan Face to Verify Age"

## Security Notes

- Always validate age on the server side
- Store verification logs
- Use HTTPS in production
- Implement rate limiting to prevent abuse
- Consider multi-factor verification for high-value transactions

## Current Demo Mode

The system currently runs in DEMO MODE which:
- Generates a random age between 18-37
- Simulates 2-second scanning delay
- Shows success/failure based on random age

This allows you to test the UI flow before connecting the actual backend.
