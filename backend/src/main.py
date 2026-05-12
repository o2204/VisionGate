import joblib

from fastapi import FastAPI

from src.routers.user_router import user_router
from src.routers.admin_router import admin_router
from src.routers.history_router import history_router
from src.routers.face_router import face_router
from src.routers.alert_router import alert_router
from src.routers.gate_router import gate_router
from src.routers.verify_router import verify_router 

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="VisionGate", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# model = joblib.load("src/VisionGateModel.h5")
model = None # Placeholder

@app.get("/")
async def root():
    return {"message": "Welcome to VisionGate"}

app.include_router(user_router)
app.include_router(admin_router)
app.include_router(history_router)
app.include_router(face_router)
app.include_router(alert_router)
app.include_router(gate_router)
app.include_router(verify_router)