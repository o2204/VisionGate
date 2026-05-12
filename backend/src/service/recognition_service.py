# app/services/recognition.py

import cv2
import numpy as np
import joblib

from insightface.app import FaceAnalysis

# Load trained classifier once
# model = joblib.load("src/VisionGateModel.h5")
model = None # Placeholder

# Load face analysis model once
face_app = FaceAnalysis()
face_app.prepare(ctx_id=0)


async def recognize_face(file):

    # Read uploaded image
    contents = await file.read()

    # Convert bytes -> OpenCV image
    nparr = np.frombuffer(contents, np.uint8)

    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Detect faces
    faces = face_app.get(img)

    # No face found
    if len(faces) == 0:
        return {
            "authorized": False,
            "message": "No face detected"
        }

    # Extract embedding
    embedding = faces[0].embedding

    # Predict identity
    prediction = model.predict([embedding])

    # Confidence score
    probabilities = model.predict_proba([embedding])

    confidence = float(np.max(probabilities))

    # Unknown person threshold
    if confidence < 0.6:
        return {
            "authorized": False,
            "message": "Unknown person"
        }

    # Authorized user
    return {
        "authorized": True,
        "name": prediction[0],
        "confidence": confidence
    }