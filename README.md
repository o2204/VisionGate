# VisionGate 🛡️

VisionGate is an advanced, AI-powered smart security and access control system. It leverages cutting-edge computer vision, facial recognition, and liveness detection to provide a secure and futuristic environment. Built with a **FastAPI** backend and a **Flutter** frontend, VisionGate offers real-time monitoring, intelligent automation, and a stunning cyberpunk-themed dashboard.

## ✨ Key Features

- **🛡️ Biometric Authentication**: State-of-the-art facial recognition for secure access.
- **👁️ Liveness Detection**: Advanced anti-spoofing to prevent unauthorized access via photos or videos.
- **⚡ Real-time Monitoring**: Live camera feeds with intruder detection and instant alerts.
- **📊 Admin Dashboard**: Comprehensive command center for user management, hardware status, and analytics.
- **📱 Cross-Platform UI**: A beautiful, cyberpunk-themed mobile/web application built with Flutter.
- **🔗 OAuth Integration**: Secure sign-in options including Google OAuth.
- **📧 Intelligent Alerts**: Automated notifications via Email and SMS for security events.

## 🛠️ Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **AI/ML**: InsightFace, OpenCV, Face Recognition, ONNX Runtime
- **Database**: PostgreSQL (via SQLAlchemy & asyncpg)
- **Security**: JWT, OAuth2, Passlib
- **Notifications**: FastAPI-Mail, Twilio

### Frontend
- **Framework**: [Flutter](https://flutter.dev/)
- **Theme**: Custom Cyberpunk UI
- **State Management**: Provider / Riverpod (as per implementation)
- **Icons**: Font Awesome / Material Symbols

## 📂 Project Structure

```text
VisionGate/
├── backend/            # FastAPI Backend Service
│   ├── src/            # Application Logic
│   ├── migrations/     # Database Migrations
│   └── requirements.txt # Python Dependencies
├── ui/                 # Flutter Frontend Applications
│   └── visiongate/     # Main Mobile/Web App
└── assets/             # Project Assets (Banners, Logos)
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Flutter SDK
- PostgreSQL
- Redis

### Backend Setup
1. Navigate to the backend directory: `cd backend`
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `.\venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/macOS)
4. Install dependencies: `pip install -r requirements.txt`
5. Configure `.env` (see `backend/README.md` for details)
6. Run migrations: `alembic upgrade head`
7. Start the server: `uvicorn src.main:app --reload`

### Frontend Setup
1. Navigate to the UI directory: `cd ui/visiongate`
2. **Download Fonts**: Ensure `Orbitron` and `Rajdhani` are placed in `assets/fonts/`.
3. Install dependencies: `flutter pub get`
4. Run the app: `flutter run`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

Built with ❤️ by the VisionGate Team.
