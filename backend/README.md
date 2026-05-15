# VisionGate Backend 🛡️

VisionGate is a sophisticated AI-powered security and access control system. The backend is built with FastAPI and leverages state-of-the-art computer vision models for secure biometric authentication, liveness detection, and real-time threat monitoring.

## 🚀 Key Features

- **Biometric Authentication**: Secure facial recognition using `insightface` and `face_recognition`.
- **Liveness Detection**: Anti-spoofing mechanisms to prevent photo/video-based unauthorized access.
- **Role-Based Access Control (RBAC)**: Distinct permissions for Admins and regular Users.
- **Intruder Detection & Alerts**: Real-time monitoring and automated alerts (Email/SMS) for unauthorized access attempts.
- **History & Logging**: Comprehensive tracking of all entry/exit events.
- **OAuth Integration**: Support for Google Sign-In.
- **Asynchronous Processing**: High-performance API built on FastAPI with asynchronous database drivers.
- **Scalable Infrastructure**: Integration with Supabase for managed database/storage and Redis for caching.

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **Database**: PostgreSQL (via [SQLAlchemy](https://www.sqlalchemy.org/) & [asyncpg](https://magicstack.github.io/asyncpg/))
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **AI/ML**: OpenCV, InsightFace, ONNX Runtime, Face Recognition
- **Security**: JWT, Passlib (Bcrypt), OAuth2
- **Notifications**: FastAPI-Mail, Twilio (SMS)
- **Cache**: Redis
- **Cloud Integration**: Supabase (PostgreSQL & Storage)

## 📁 Project Structure

```text
backend/
├── src/
│   ├── core/           # Configuration, security, and utility functions
│   ├── models/         # SQLAlchemy database models
│   ├── schemas/        # Pydantic models for request/response validation
│   ├── routers/        # API endpoints (User, Admin, Face, etc.)
│   ├── service/        # Business logic and AI service wrappers
│   ├── media/          # Static assets and uploaded images
│   ├── main.py         # Application entry point
│   └── VisionGateModel.h5 # Trained AI models
├── migrations/         # Alembic database migration scripts
├── requirements.txt    # Python dependencies
└── alembic.ini         # Alembic configuration
```

## ⚙️ Prerequisites

- Python 3.10 or higher
- Redis server
- PostgreSQL (or Supabase account)
- Virtual Environment (`venv` or `conda`)

## 🛠️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd VisionGate/backend
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Create a `.env` file in the `backend` directory and populate it with the following:

   ```env
   # Database
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/visiongate

   # Supabase
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key

   # JWT
   JWT_SECRET=your_super_secret_key
   JWT_ALGORITHM=HS256

   # Redis
   REDIS_HOST=localhost
   REDIS_PORT=6379

   # OAuth
   CLIENT_ID=your_google_client_id
   CLIENT_SECRET=your_google_client_secret

   # Notifications
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   MAIL_FROM=your_email@gmail.com
   MAIL_FROM_NAME=VisionGate Admin
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587

   # Twilio
   TWILIO_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   TWILIO_NUMBER=your_twilio_phone_number
   ```

5. **Run Migrations**:
   ```bash
   alembic upgrade head
   ```

## 🏃 Running the Application

Start the FastAPI server using Uvicorn:

```bash
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`.

### 📖 API Documentation

Once the server is running, you can access the interactive documentation at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🛡️ Security Note

- Ensure the `JWT_SECRET` is kept private and never committed to version control.
- Use environment-specific `.env` files for production.
- Facial biometric data is stored securely using embeddings rather than raw images where possible.

## GitHub Link: 
## 🤝 Contributing

1. Fork the project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.
